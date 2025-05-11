import json
import logging
import time
import threading
from enum import Enum
from typing import Dict, Optional, List
from datetime import datetime

class AccessStatus(Enum):
    """출입 상태 열거형"""
    ENTRY = "entry"      # 입장
    EXIT = "exit"        # 퇴장
    DENIED = "denied"    # 거부

class AccessController:
    """출입 관리 컨트롤러 클래스
    
    출입 제어 시스템의 비즈니스 로직을 처리하는 클래스입니다.
    RFID 인식, 출입문 제어, 출입 기록 관리 등의 기능을 제공합니다.
    """
    
    def __init__(self, tcp_handler, websocket_manager, db_helper=None):
        """출입 관리 컨트롤러 초기화
        
        Args:
            tcp_handler: TCP 통신 핸들러
            websocket_manager: WebSocket 통신 관리자
            db_helper: 데이터베이스 헬퍼
        """
        self.tcp_handler = tcp_handler
        self.ws_manager = websocket_manager
        self.db = db_helper
        self.logger = logging.getLogger(__name__)
        
        # 등록된 직원 정보 (임시, 실제로는 DB에서 관리)
        self.employees = {
            "E39368F5": {"id": "E39368F5", "name": "김민준", "department": "물류팀", "access": True},
            "E47291A3": {"id": "E47291A3", "name": "이서연", "department": "품질관리팀", "access": True},
            "E58213F7": {"id": "E58213F7", "name": "박지훈", "department": "외부인", "access": False}
        }
        
        # 출입 기록
        self.access_logs = []
        
        # 출입문 상태
        self.door_open = False
        self.door_timer = None
        
    def handle_message(self, message: Dict):
        """TCP 메시지 처리
        
        Args:
            message (Dict): 메시지 데이터
        """
        try:
            if message.get('tp') == 'evt':
                if message.get('evt') == 'rfid':
                    # RFID 태그 이벤트 처리
                    self.process_rfid(message.get('val', {}))
            elif message.get('tp') == 'res':
                # 응답 메시지 처리
                self.handle_response(message)
                
        except Exception as e:
            self.logger.error(f"메시지 처리 중 오류 발생: {str(e)}")
            
    def process_rfid(self, rfid_data: Dict):
        """RFID 태그 처리
        
        Args:
            rfid_data (Dict): RFID 데이터
        """
        try:
            rfid_uid = rfid_data.get('uid')
            if not rfid_uid:
                self.logger.error("RFID UID가 없습니다.")
                return
                
            # 직원 정보 조회
            employee = self.employees.get(rfid_uid)
            
            # 인증 및 출입문 제어
            if employee and employee["access"]:
                # 승인된 직원 - 출입문 열기
                access_status = AccessStatus.ENTRY
                self.control_door(True)
                
                # GUI 업데이트
                self.update_gui({
                    "employee": employee,
                    "status": access_status.value,
                    "timestamp": datetime.now().isoformat()
                })
                
                # 출입 기록 저장
                self.log_access(employee, access_status)
                
                self.logger.info(f"출입 승인: {employee['name']} ({employee['department']})")
            else:
                # 미등록 직원 또는 출입 권한 없음
                self.handle_unauthorized_access(rfid_uid)
                
        except Exception as e:
            self.logger.error(f"RFID 처리 중 오류 발생: {str(e)}")
            
    def handle_unauthorized_access(self, rfid_uid: str):
        """미등록 또는 권한 없는 출입 처리
        
        Args:
            rfid_uid (str): RFID UID
        """
        try:
            # 미등록 직원 정보 생성
            employee = {
                "id": rfid_uid,
                "name": "미등록 사용자",
                "department": "알 수 없음",
                "access": False
            }
            
            # 출입 거부
            self.logger.warning(f"출입 거부: 미등록 또는 권한 없음 ({rfid_uid})")
            
            # 출입 기록 저장
            self.log_access(employee, AccessStatus.DENIED)
            
            # GUI 업데이트 - 경고 표시
            self.update_gui({
                "employee": employee,
                "status": AccessStatus.DENIED.value,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"미등록 출입 처리 중 오류 발생: {str(e)}")
            
    def authorize_access(self, employee: Dict, access_status: AccessStatus) -> bool:
        """출입 승인 및 제어
        
        Args:
            employee (Dict): 직원 정보
            access_status (AccessStatus): 출입 상태
            
        Returns:
            bool: 승인 결과
        """
        if not employee or not employee.get("access"):
            return False
            
        # 출입문 제어
        if access_status == AccessStatus.ENTRY or access_status == AccessStatus.EXIT:
            self.control_door(True)
            return True
        else:
            return False
            
    def control_door(self, open_door: bool):
        """출입문 제어
        
        Args:
            open_door (bool): 출입문 열기 여부
        """
        try:
            # 현재 출입문 상태가 이미 요청과 동일하면 무시
            if self.door_open == open_door:
                return
                
            # 출입문 제어 명령 전송
            message = {
                "dev": "gt",
                "tp": "cmd",
                "cmd": "door",
                "act": "open" if open_door else "close"
            }
            self.tcp_handler.send_message("gt", message)
            
            # 상태 업데이트
            self.door_open = open_door
            
            if open_door:
                # 일정 시간 후 자동으로 닫기
                self.set_door_timer()
                
            self.logger.info(f"출입문 {'열림' if open_door else '닫힘'}")
            
        except Exception as e:
            self.logger.error(f"출입문 제어 중 오류 발생: {str(e)}")
            
    def set_door_timer(self):
        """출입문 타이머 설정 (자동 닫힘)"""
        # 기존 타이머 취소
        if self.door_timer:
            self.door_timer.cancel()
            
        # 새 타이머 설정
        self.door_timer = threading.Timer(2.0, self.close_door)
        self.door_timer.daemon = True
        self.door_timer.start()
            
    def close_door(self):
        """출입문 닫기"""
        self.control_door(False)
            
    def log_access(self, employee: Dict, access_status: AccessStatus):
        """출입 기록 저장
        
        Args:
            employee (Dict): 직원 정보
            access_status (AccessStatus): 출입 상태
        """
        log_entry = {
            "employee_id": employee["id"],
            "name": employee["name"],
            "department": employee["department"],
            "status": access_status.value,
            "timestamp": datetime.now().isoformat()
        }
        
        # 로컬 기록 저장
        self.access_logs.append(log_entry)
        
        # DB 저장 (있는 경우)
        if self.db:
            self.db.save_access_log(log_entry)
            
    def handle_response(self, response_data: Dict):
        """응답 메시지 처리
        
        Args:
            response_data (Dict): 응답 데이터
        """
        status = response_data.get('res')
        if status == 'ok':
            self.logger.info("명령 실행 성공")
        else:
            error_code = response_data.get('val', {}).get('c')
            error_msg = response_data.get('val', {}).get('m')
            self.logger.error(f"명령 실행 실패: {error_code} - {error_msg}")
            
    def update_gui(self, additional_data: Dict = None):
        """GUI 업데이트
        
        Args:
            additional_data (Dict, optional): 추가 데이터
        """
        status_data = {
            "door_open": self.door_open,
            "total_entries": len([log for log in self.access_logs if log["status"] == AccessStatus.ENTRY.value]),
            "total_exits": len([log for log in self.access_logs if log["status"] == AccessStatus.EXIT.value]),
            "recent_logs": self.access_logs[-5:] if self.access_logs else []
        }
        
        if additional_data:
            status_data.update(additional_data)
            
        # WebSocket으로 상태 브로드캐스트
        self.ws_manager.broadcast("access_status", status_data)
        
    def get_access_logs(self, date: str = None) -> Dict:
        """출입 기록 조회
        
        Args:
            date (str, optional): 조회할 날짜 (YYYY-MM-DD)
            
        Returns:
            Dict: 출입 기록 정보
        """
        # 날짜 필터링 (옵션)
        filtered_logs = self.access_logs
        if date:
            filtered_logs = [
                log for log in self.access_logs 
                if log["timestamp"].startswith(date)
            ]
            
        return {
            "total_entry": len([log for log in filtered_logs if log["status"] == AccessStatus.ENTRY.value]),
            "total_exit": len([log for log in filtered_logs if log["status"] == AccessStatus.EXIT.value]),
            "total_denied": len([log for log in filtered_logs if log["status"] == AccessStatus.DENIED.value]),
            "current_count": len([log for log in filtered_logs if log["status"] == AccessStatus.ENTRY.value]) - 
                            len([log for log in filtered_logs if log["status"] == AccessStatus.EXIT.value]),
            "logs": filtered_logs
        }
        
    def open_door(self) -> bool:
        """출입문 수동 열기
        
        Returns:
            bool: 성공 여부
        """
        try:
            self.control_door(True)
            return True
        except Exception as e:
            self.logger.error(f"출입문 열기 실패: {str(e)}")
            return False
