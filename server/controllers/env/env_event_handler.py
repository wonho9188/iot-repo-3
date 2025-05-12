import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# ==== 환경 이벤트 처리 클래스 ====
class EnvEventHandler:
    # ==== 이벤트 핸들러 초기화 ====
    def __init__(self, controller, tcp_handler):
        self.controller = controller
        self.tcp_handler = tcp_handler
        
        logger.info("환경 이벤트 핸들러 초기화 완료")
    
    # ==== 이벤트 메시지 처리 ====
    def handle_event(self, message: Dict[str, Any]):
        """이벤트 메시지를 처리합니다."""
        try:
            # 메시지 콘텐츠 확인
            content = message.get('content', '')
            
            # 이벤트 타입별 처리
            if content.startswith('tp'):
                # 온도 이벤트
                self._handle_temperature_event(content)
            elif content.startswith('wA'):
                # A 창고 경고
                self._handle_warning_event('A', content)
            elif content.startswith('wB'):
                # B 창고 경고
                self._handle_warning_event('B', content)
            elif content.startswith('wC'):
                # C 창고 경고
                self._handle_warning_event('C', content)
            else:
                logger.warning(f"알 수 없는 이벤트 콘텐츠: {content}")
        
        except Exception as e:
            logger.error(f"환경 이벤트 처리 중 오류: {str(e)}")
    
    # ==== 응답 메시지 처리 ====
    def handle_response(self, message: Dict[str, Any]):
        """응답 메시지를 처리합니다."""
        try:
            # 응답 콘텐츠 확인
            content = message.get('content', '')
            
            # 응답 타입별 처리
            if content.startswith('ok'):
                # 성공 응답
                logger.debug(f"환경 제어 성공 응답: {content}")
            else:
                logger.warning(f"알 수 없는 응답 콘텐츠: {content}")
        
        except Exception as e:
            logger.error(f"환경 응답 처리 중 오류: {str(e)}")
    
    # ==== 오류 메시지 처리 ====
    def handle_error(self, message: Dict[str, Any]):
        """오류 메시지를 처리합니다."""
        try:
            # 오류 콘텐츠 확인
            content = message.get('content', '')
            
            # 오류 코드 추출
            error_code = content[1:] if len(content) > 1 else "unknown"
            
            logger.error(f"환경 제어 오류: {error_code}")
            
            # 웹소켓 이벤트 발송
            self.controller._emit_socketio_event("environment_error", {
                "error_code": error_code,
                "error_message": f"환경 제어 오류: {error_code}"
            })
        
        except Exception as e:
            logger.error(f"환경 오류 처리 중 오류: {str(e)}")
    
    # ==== 온도 이벤트 처리 ====
    def _handle_temperature_event(self, content: str):
        """온도 이벤트를 처리합니다."""
        # 값 추출 (tp-18.5;4.2;21.3 - 세미콜론으로 구분된 3개의 온도)
        if len(content) < 3:
            logger.warning(f"잘못된 온도 이벤트 형식: {content}")
            return
        
        # 온도 값 추출 (tp- 이후의 값)
        temp_data = content[3:]
        
        # 세미콜론으로 구분된 온도 값들 파싱
        temps = temp_data.split(';')
        
        updates = []
        
        # 각 창고별 온도 할당 (창고 순서는 A, B, C 순으로 가정)
        warehouses = ['A', 'B', 'C']
        
        for i, temp_str in enumerate(temps):
            if i >= len(warehouses):
                break
                
            try:
                temp = float(temp_str)
                warehouse = warehouses[i]
                
                # 온도 업데이트
                update_result = self.controller.update_temperature(warehouse, temp)
                
                if update_result:
                    updates.append(update_result)
                    
                    # 알람 상태 업데이트만 유지 (팬 제어 호출 제거)
                    self._handle_alarm_status(warehouse, update_result["state"])
            
            except ValueError:
                logger.warning(f"잘못된 온도 값 형식: {temp_str}")
        
        # 모든 업데이트가 완료되면 상태 변경 이벤트 발송
        if updates:
            self.controller._update_status()
    
    # ==== 경고 이벤트 처리 ====
    def _handle_warning_event(self, warehouse: str, content: str):
        """창고 경고 이벤트를 처리합니다."""
        # 값 추출 (wA1 - A 창고 경고 상태 1)
        if len(content) < 3:
            logger.warning(f"잘못된 경고 이벤트 형식: {content}")
            return
        
        # 경고 상태 추출 (마지막 문자)
        try:
            warning_state = int(content[2:])
            
            # 상태 업데이트
            self.controller.temp_controller.update_warning(warehouse, warning_state == 1)
            
            # 웹소켓 이벤트 발송
            self.controller._emit_socketio_event("warehouse_warning", {
                "warehouse": warehouse,
                "warning": warning_state == 1
            })
            
            # 전체 상태 업데이트
            self.controller._update_status()
            
        except ValueError:
            logger.warning(f"잘못된 경고 상태 값: {content[2:]}")

    # ==== 알람 상태 처리 ====
    def _handle_alarm_status(self, warehouse: str, state: str):
        """창고의 알람 상태를 처리합니다."""
        alarm_state = "norm"
        
        if state == "warning":
            alarm_state = "warn"
        elif state == "danger":
            alarm_state = "dang"
        
        # 알람 설정 - 내부 상태만 업데이트
        self.controller.temp_controller.set_alarm(warehouse, alarm_state)

    # ==== 팬 제어 업데이트 ====
    def _update_fan_control(self, warehouse: str, update: Dict[str, Any]):
        """창고의 팬 제어를 업데이트합니다."""
        # 펌웨어에서 자체적으로 처리하므로 비활성화
        pass