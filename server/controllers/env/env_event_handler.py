import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# ==== 환경 이벤트 처리 클래스 ====
class EnvEventHandler:
    # ==== 이벤트 핸들러 초기화 ====
    def __init__(self, controller, tcp_handler):
        self.controller = controller
        self.tcp_handler = tcp_handler
        
        # 핸들러 맵 초기화 - 이벤트 타입별 처리 메소드 매핑
        self.event_handlers = {
            "tmp": self._handle_temperature_event
        }
        
        # 응답 핸들러 맵
        self.response_handlers = {
            "ok": self._handle_ok_response,
            "err": self._handle_error_response
        }
        
        logger.info("환경 이벤트 핸들러 초기화 완료")
    
    # ==== 이벤트 메시지 처리 ====
    def handle_event(self, message: Dict[str, Any]):
        """이벤트 메시지를 핸들러 맵을 사용하여 처리합니다."""
        try:
            if 'evt' not in message or 'val' not in message:
                logger.warning(f"잘못된 이벤트 메시지 형식: {json.dumps(message)}")
                return
            
            event_type = message['evt']
            values = message['val']
            
            # 핸들러 맵에서 처리 메소드 검색 및 실행
            if event_type in self.event_handlers:
                self.event_handlers[event_type](values)
            else:
                logger.warning(f"알 수 없는 이벤트 타입: {event_type}")
        
        except Exception as e:
            logger.error(f"환경 이벤트 처리 중 오류: {str(e)}")
    
    # ==== 응답 메시지 처리 ====
    def handle_response(self, message: Dict[str, Any]):
        """응답 메시지를 핸들러 맵을 사용하여 처리합니다."""
        try:
            if 'res' not in message:
                logger.warning(f"잘못된 응답 메시지 형식: {json.dumps(message)}")
                return
            
            response_type = message['res']
            values = message.get('val', {})
            
            # 핸들러 맵에서 처리 메소드 검색 및 실행
            if response_type in self.response_handlers:
                self.response_handlers[response_type](values)
            else:
                logger.warning(f"알 수 없는 응답 타입: {response_type}")
        
        except Exception as e:
            logger.error(f"환경 응답 처리 중 오류: {str(e)}")
    
    # ==== 온도 이벤트 처리 ====
    def _handle_temperature_event(self, values: Dict[str, Any]):
        """온도 이벤트를 처리합니다."""
        updates = []
        
        # 각 창고별 온도 업데이트
        for warehouse in ["A", "B", "C", "D"]:
            if warehouse in values:
                wh_data = values[warehouse]
                
                # 온도 값 확인
                if 't' in wh_data:
                    temp = wh_data['t']
                    
                    # 상태 정보 처리
                    status = wh_data.get('st', 'norm')
                    
                    # 컨트롤러를 통해 온도 업데이트
                    update_result = self.controller.update_temperature(warehouse, temp)
                    
                    if update_result:
                        updates.append(update_result)
                        
                        # 알람 상태 업데이트
                        self._handle_alarm_status(warehouse, update_result["state"])
                        
                        # 팬 제어 실행
                        self._update_fan_control(warehouse, update_result)
                        
                        # 제습기 제어 (C, D 창고만)
                        if warehouse in ["C", "D"] and "humidity" in wh_data:
                            humidity = wh_data["humidity"]
                            # 습도 60% 초과시 제습기 켜기
                            if humidity > 60:
                                self.controller.temp_controller.set_dehumidifier(warehouse, True)
                            else:
                                self.controller.temp_controller.set_dehumidifier(warehouse, False)
        
        # 모든 업데이트가 완료되면 상태 변경 이벤트 발송
        if updates:
            self.controller._update_status()
    
    # ==== 알람 상태 처리 ====
    def _handle_alarm_status(self, warehouse: str, state: str):
        """창고의 알람 상태를 처리합니다."""
        alarm_state = "norm"
        
        if state == "warning":
            alarm_state = "warn"
        elif state == "danger":
            alarm_state = "dang"
        
        # 알람 설정
        self.controller.temp_controller.set_alarm(warehouse, alarm_state)
    
    # ==== 팬 제어 업데이트 ====
    def _update_fan_control(self, warehouse: str, update: Dict[str, Any]):
        """창고의 팬 제어를 업데이트합니다."""
        # 팬 모드 및 속도 확인
        fan_mode = update.get("fan_mode")
        fan_speed = update.get("fan_speed")
        
        if fan_mode and fan_speed is not None:
            # 팬 설정 명령 전송
            self.controller.temp_controller.set_fan(warehouse, fan_mode, fan_speed)
    
    # ==== 성공 응답 처리 ====
    def _handle_ok_response(self, values: Dict[str, Any]):
        """성공 응답을 처리합니다."""
        # 디버그 로그만 기록
        logger.debug(f"환경 제어 성공 응답: {json.dumps(values)}")
        
        # 추가 처리가 필요한 경우 구현
    
    # ==== 오류 응답 처리 ====
    def _handle_error_response(self, values: Dict[str, Any]):
        """오류 응답을 처리합니다."""
        # 각 창고별 오류 처리
        for warehouse in ["A", "B", "C", "D"]:
            if warehouse in values and values[warehouse]:
                error_data = values[warehouse]
                error_code = error_data.get('c', 'unknown')
                error_message = error_data.get('m', '알 수 없는 오류')
                
                logger.error(f"창고 {warehouse} 환경 제어 오류: {error_code}, {error_message}")
                
                # 웹소켓 이벤트 발송
                self.controller._emit_socketio_event("environment_error", {
                    "warehouse": warehouse,
                    "error_code": error_code,
                    "error_message": error_message
                })