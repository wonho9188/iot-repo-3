# server/controllers/sort_controller.py
import logging
import time
from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime

# 내부 모듈 임포트
from .sort_event_handler import SortEventHandler
from .shelf_manager import ShelfManager

logger = logging.getLogger(__name__)

# ==== 분류기 상태 열거형 ====
class SortStatus(Enum):
    STOPPED = "stopped"           # 정지 상태
    RUNNING = "running"           # 실행 중
    EMERGENCY_STOP = "emergency"  # 비상 정지

# ==== 물류 분류 시스템 컨트롤러 ====
class SortController:
    # ==== 분류기 컨트롤러 초기화 ====
    def __init__(self, tcp_handler, socketio=None, db_helper=None):
        self.tcp_handler = tcp_handler
        self.socketio = socketio
        
        # 상태 변수
        self.status = SortStatus.STOPPED.value
        self.physical_emergency = False
        self.motor_active = False
        
        # 물품 카운터
        self.items_waiting = 0
        self.items_processed = 0
        
        # 분류대별 물품 수 카운터
        self.sorted_items = {
            "A": 0,  # 냉동
            "B": 0,  # 냉장
            "C": 0,  # 상온
            "D": 0,  # 비식품
            "E": 0   # 오류물품
        }
        
        # 분류 기록 로그 (최근 10개)
        self.sort_logs = []
        
        # 선반 관리자 생성
        self.shelf_manager = ShelfManager(db_helper)
        
        # 이벤트 핸들러 생성
        self.event_handler = SortEventHandler(self, tcp_handler, self.shelf_manager)
        
        # TCP 핸들러에 이벤트 리스너 등록
        self._register_tcp_handlers()
        
        logger.info("분류기 컨트롤러 초기화 완료")
    
    # ==== TCP 핸들러에 이벤트 리스너 등록 ====
    def _register_tcp_handlers(self):
        # 분류기(sr) 디바이스의 이벤트 핸들러 등록
        self.tcp_handler.register_device_handler("sr", "evt", self.event_handler.handle_event)
        # 응답(res) 타입 핸들러
        self.tcp_handler.register_device_handler("sr", "res", self.event_handler.handle_response)
    
    # ==== 분류 작업 시작 ====
    def start_sorting(self) -> dict:
        # 물리적 비상정지 상태 확인
        if self.physical_emergency:
            return {
                "status": "error",
                "code": "E3001",
                "message": "물리적 비상정지 버튼이 활성화되어 있습니다. 버튼을 해제해주세요.",
                "auto_dismiss": 1000
            }
        
        # 이미 작동 중인지 확인
        if self.status == SortStatus.RUNNING.value:
            return {
                "status": "error",
                "code": "E3002",
                "message": "이미 작동 중입니다",
                "auto_dismiss": 1000
            }
        
        # 시작 명령 전송
        command = {
            "dev": "sr",
            "tp": "cmd",
            "cmd": "inb",
            "act": "start"
        }
        
        success = self.tcp_handler.send_message("sr", command)
        if not success:
            return {
                "status": "error",
                "code": "E3003",
                "message": "분류기 통신 오류",
                "auto_dismiss": 1000
            }
        
        # 상태 업데이트
        self.status = SortStatus.RUNNING.value
        self.motor_active = True
        self.items_waiting = 0
        self.items_processed = 0
        
        # 상태 업데이트 이벤트 발송
        self._update_status()
        
        # 자동 정지 타이머 초기화
        self.event_handler.reset_auto_stop_timer()
        
        return {
            "status": "ok",
            "device_status": "running",
            "message": "분류기 작동을 시작합니다."
        }
    
    # ==== 분류 작업 정지 ====
    def stop_sorting(self) -> dict:
        # 작동 중인지 확인
        if self.status != SortStatus.RUNNING.value:
            return {
                "status": "error",
                "code": "E3004",
                "message": "분류기가 작동 중이 아닙니다",
                "auto_dismiss": 1000
            }
        
        # 대기 물품이 있는지 확인
        if self.items_waiting > 0:
            return {
                "status": "error",
                "code": "E3005",
                "message": "아직 처리 중인 물품이 있습니다",
                "auto_dismiss": 1000
            }
        
        # 정지 명령 전송
        command = {
            "dev": "sr",
            "tp": "cmd",
            "cmd": "inb",
            "act": "stop"
        }
        
        success = self.tcp_handler.send_message("sr", command)
        if not success:
            return {
                "status": "error",
                "code": "E3003",
                "message": "분류기 통신 오류",
                "auto_dismiss": 1000
            }
        
        # 상태 업데이트
        self.status = SortStatus.STOPPED.value
        self.motor_active = False
        
        # 자동 정지 타이머 취소
        self.event_handler.cancel_auto_stop_timer()
        
        # 상태 업데이트 이벤트 발송
        self._update_status()
        
        return {
            "status": "ok",
            "device_status": "stopped",
            "message": "분류기 작동을 정지합니다."
        }
    
    # ==== 비상 정지 실행 ====
    def emergency_stop(self) -> dict:
        # 비상 정지 명령 전송
        command = {
            "dev": "sr",
            "tp": "cmd",
            "cmd": "em",
            "act": "stop",
            "val": {
                "pr": "hi"
            }
        }
        
        success = self.tcp_handler.send_message("sr", command)
        if not success:
            return {
                "status": "error",
                "code": "E3003",
                "message": "분류기 통신 오류",
                "auto_dismiss": 1000
            }
        
        # 상태 업데이트
        self.status = SortStatus.EMERGENCY_STOP.value
        self.motor_active = False
        
        # 자동 정지 타이머 취소
        self.event_handler.cancel_auto_stop_timer()
        
        # 상태 업데이트 이벤트 발송
        self._update_status()
        
        # 웹소켓 이벤트 발송
        self._emit_socketio_event("emergency_stop", {
            "physical_button": False,
            "status": self.status
        })
        
        return {
            "status": "ok",
            "device_status": "emergency_stopped",
            "message": "비상 정지가 실행되었습니다."
        }
    
    # ==== 현재 분류기 상태 반환 ====
    def check_status(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "physical_emergency": self.physical_emergency,
            "motor_active": self.motor_active,
            "items_waiting": self.items_waiting,
            "items_processed": self.items_processed,
            "sorted_items": self.sorted_items,
            "timestamp": datetime.now().isoformat()
        }
    
    # ==== 현재 분류기 상태 반환 (check_status와 동일 기능) ====
    def get_status(self) -> dict:
        return self.check_status()
    
    # ==== 분류기 상태 업데이트 및 Socket.IO 이벤트 발송 ====
    def _update_status(self):
        status_data = {
            "status": self.status,
            "items_waiting": self.items_waiting,
            "items_processed": self.items_processed,
            "sorted_items": self.sorted_items,
            "physical_emergency": self.physical_emergency,
            "motor_active": self.motor_active,
            "timestamp": datetime.now().isoformat()
        }
        
        # Socket.IO 이벤트 발송
        self._emit_socketio_event("sorter_status", status_data)
    
    # ==== Socket.IO 이벤트 발송 ====
    def _emit_socketio_event(self, event_type: str, data: dict):
        if not self.socketio:
            logger.warning(f"Socket.IO 없음 - 이벤트 발송 불가: {event_type}")
            return
        try:
            # Flask-SocketIO 포맷으로 이벤트 발송
            self.socketio.emit("event", {
                "type": "event",
                "category": "sorter",
                "action": event_type,
                "payload": data,
                "timestamp": int(time.time())
            })
            logger.debug(f"Socket.IO 이벤트 발송: {event_type}")
        except Exception as e:
            logger.error(f"Socket.IO 이벤트 발송 오류: {str(e)}")