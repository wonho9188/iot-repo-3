import logging
import time
from typing import Dict, Any
from datetime import datetime

# 내부 모듈 임포트
from .env_status import EnvStatus
from .env_event_handler import EnvEventHandler
from .temp_controller import TempController

logger = logging.getLogger(__name__)

# ==== 환경 제어 컨트롤러 ====
class EnvController:
    # ==== 환경 컨트롤러 초기화 ====
    def __init__(self, tcp_handler, socketio=None, db_helper=None):
        self.tcp_handler = tcp_handler
        self.socketio = socketio
        self.db_helper = db_helper
        
        # 상태 관리자 생성
        self.status_manager = EnvStatus(self)
        
        # 온도 제어 모듈 생성
        self.temp_controller = TempController(tcp_handler)
        
        # 이벤트 핸들러 생성
        self.event_handler = EnvEventHandler(self, tcp_handler)
        
        # TCP 핸들러에 이벤트 리스너 등록
        self._register_tcp_handlers()
        
        logger.info("환경 컨트롤러 초기화 완료")
    
    # ==== TCP 핸들러에 이벤트 리스너 등록 ====
    def _register_tcp_handlers(self):
        """TCP 핸들러에 콜백 함수를 등록합니다."""
        # 환경 제어 컨트롤러(H)의 이벤트 핸들러 등록
        self.tcp_handler.register_device_handler("env_controller", "evt", self.event_handler.handle_event)
        
        # 응답(res) 타입 핸들러
        self.tcp_handler.register_device_handler("env_controller", "res", self.event_handler.handle_response)
        
        # 오류(err) 타입 핸들러
        self.tcp_handler.register_device_handler("env_controller", "err", self.event_handler.handle_error)
        
        logger.debug("TCP 핸들러에 이벤트 리스너 등록 완료")
    
    # ==== 온도 업데이트 ====
    def update_temperature(self, warehouse: str, temp: float) -> Dict[str, Any]:
        """특정 창고의 온도를 업데이트하고 새 상태를 반환합니다."""
        return self.status_manager.update_temperature(warehouse, temp)
    
    # ==== 목표 온도 설정 ====
    def set_target_temperature(self, warehouse: str, temperature: float) -> dict:
        """특정 창고의 목표 온도를 설정합니다."""
        if warehouse not in self.temp_controller.warehouses:
            return {
                "status": "error",
                "code": "E4001",
                "message": f"존재하지 않는 창고: {warehouse}",
                "auto_dismiss": 1000
            }
        
        # 유효 범위 확인
        min_temp, max_temp = self.temp_controller.get_temperature_range(warehouse)
        if temperature < min_temp or temperature > max_temp:
            return {
                "status": "error",
                "code": "E4002",
                "message": f"유효하지 않은 온도 값: {temperature}. 범위는 {min_temp}~{max_temp}입니다.",
                "auto_dismiss": 1000
            }
        
        # 온도 설정 명령 전송
        # HCpA-20\n - 하우스(H) 명령(C) 온도설정(p) A창고(A) -20도(-20)
        value = int(temperature)  # 정수로 변환 (소수점 버림)
        command = f"HCp{warehouse}{value}\n"
        
        success = self.tcp_handler.send_message("env_controller", command)
        if not success:
            return {
                "status": "error",
                "code": "E4003",
                "message": "환경 제어 통신 오류",
                "auto_dismiss": 1000
            }
        
        # 내부 상태 업데이트
        self.temp_controller.set_target_temperature(warehouse, temperature)
        
        # 상태 업데이트 이벤트 발송
        self._update_status()
        
        return {
            "status": "ok",
            "warehouse": warehouse,
            "target_temperature": temperature,
            "message": f"{warehouse} 창고 목표 온도를 {temperature}도로 설정했습니다."
        }
    
    # ==== 현재 환경 상태 반환 ====
    def check_status(self) -> Dict[str, Any]:
        """현재 전체 환경 상태 정보를 반환합니다."""
        status_data = self.status_manager.get_status_data()
        status_data["timestamp"] = datetime.now().isoformat()
        
        return status_data
    
    # ==== 현재 환경 상태 반환 (API용) ====
    def get_status(self) -> dict:
        """API 응답용 상태 정보를 반환합니다."""
        status_data = self.check_status()
        
        return {
            "status": "ok",
            "data": status_data
        }
    
    # ==== 특정 창고의 환경 상태 반환 ====
    def get_warehouse_status(self, warehouse: str) -> Dict[str, Any]:
        """특정 창고의 환경 상태를 반환합니다."""
        if warehouse not in ["A", "B", "C"]:
            return {
                "status": "error",
                "code": "E4001",
                "message": f"알 수 없는 창고 ID: {warehouse}"
            }
        
        status_data = self.status_manager.get_status_data()
        if warehouse in status_data["warehouses"]:
            return {
                "status": "ok",
                "warehouse": warehouse,
                "data": status_data["warehouses"][warehouse],
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "error",
                "code": "E4003",
                "message": f"창고 {warehouse} 데이터 없음"
            }
    
    # ==== 온도 기록 저장 ====
    def log_temperature_data(self, save_to_db: bool = True) -> bool:
        """현재 온도 데이터를 로그에 기록하고 선택적으로 DB에 저장합니다."""
        status_data = self.status_manager.get_status_data()
        timestamp = datetime.now()
        
        # 로그에 각 창고의 온도 기록
        for warehouse, data in status_data["warehouses"].items():
            temp = data.get("temp")
            if temp is not None:
                logger.info(f"[{timestamp.isoformat()}] 창고 {warehouse} 온도: {temp}°C, 상태: {data.get('status')}")
                
                # DB에 기록 저장
                if save_to_db and self.db_helper:
                    try:
                        # 이상치만 저장하거나 정상 범위의 경우 시간당 한 번만 저장
                        if data.get('status') != 'normal' or timestamp.minute == 0:
                            self.db_helper.save_temperature_log(
                                warehouse,
                                temp,
                                data.get('status'),
                                timestamp
                            )
                    except Exception as e:
                        logger.error(f"온도 로그 저장 중 오류: {str(e)}")
                        return False
        
        return True
    
    # ==== 환경 상태 업데이트 및 Socket.IO 이벤트 발송 ====
    def _update_status(self):
        """현재 상태를 Socket.IO를 통해 클라이언트에 전송합니다."""
        status_data = self.status_manager.get_status_data()
        status_data["timestamp"] = datetime.now().isoformat()
        
        # Socket.IO 이벤트 발송
        self._emit_socketio_event("environment_status", status_data)
        
        # 온도 이상 상태 처리
        for warehouse, data in status_data["warehouses"].items():
            if data.get("status") in ["warning", "danger"] and data.get("temp") is not None:
                self._emit_socketio_event("temperature_alert", {
                    "warehouse": warehouse,
                    "temp": data.get("temp"),
                    "status": data.get("status"),
                    "target_temp": data.get("target_temp")
                })
    
    # ==== Socket.IO 이벤트 발송 ====
    def _emit_socketio_event(self, event_type: str, data: dict):
        """Socket.IO를 통해 이벤트를 발송합니다."""
        if not self.socketio:
            logger.warning(f"Socket.IO 없음 - 이벤트 발송 불가: {event_type}")
            return
        
        try:
            # Flask-SocketIO 포맷으로 이벤트 발송
            self.socketio.emit("event", {
                "type": "event",
                "category": "environment",
                "action": event_type,
                "payload": data,
                "timestamp": int(time.time())
            })
            logger.debug(f"Socket.IO 이벤트 발송: {event_type}")
        except Exception as e:
            logger.error(f"Socket.IO 이벤트 발송 오류: {str(e)}")
    
    # ==== 주기적 온도 로깅 함수 ====
    def schedule_temperature_logging(self, interval: int = 3600):
        """주기적으로 온도 데이터를 DB에 기록합니다 (기본 1시간)."""
        # 정시에 기록
        if datetime.now().minute == 0:
            self.log_temperature_data(True)
        
        # 자동 실행 예약
        import threading
        timer = threading.Timer(interval, self.schedule_temperature_logging, [interval])
        timer.daemon = True
        timer.start()