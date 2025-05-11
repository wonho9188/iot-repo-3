# server/controllers/env/temp_controller.py
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# ==== 온도 제어 클래스 ====
class TempController:
    # ==== 온도 제어 초기화 ====
    def __init__(self, tcp_handler):
        self.tcp_handler = tcp_handler
        
        # 창고별 알람 상태
        self.alarm_status = {
            "A": False,
            "B": False,
            "C": False,
            "D": False
        }
        
        logger.info("온도 제어 모듈 초기화 완료")
    
    # ==== 팬 제어 명령 전송 ====
    def set_fan(self, warehouse: str, mode: str, speed: int) -> bool:
        """특정 창고의 팬 모드와 속도를 설정합니다."""
        # 창고 ID 유효성 확인
        if warehouse not in ["A", "B", "C", "D"]:
            logger.warning(f"알 수 없는 창고 ID: {warehouse}")
            return False
        
        # 창고에 따른 device ID 결정
        device_id = "hs_ab" if warehouse in ["A", "B"] else "hs_cd"
        
        # 모드 유효성 확인
        if mode not in ["cool", "heat", "off"]:
            logger.warning(f"알 수 없는 팬 모드: {mode}")
            return False
        
        # 속도 유효성 확인
        if not (0 <= speed <= 3):
            logger.warning(f"유효하지 않은 팬 속도: {speed}")
            return False
        
        # 명령 구성
        command = {
            "dev": device_id,
            "tp": "cmd",
            "cmd": "fan",
            "act": "set",
            "val": {
                warehouse: {
                    "sp": speed,
                    "md": mode
                }
            }
        }
        
        # 명령 전송
        success = self.tcp_handler.send_message(device_id, command)
        
        if success:
            logger.debug(f"창고 {warehouse} 팬 설정 명령 전송 성공: 모드={mode}, 속도={speed}")
        else:
            logger.error(f"창고 {warehouse} 팬 설정 명령 전송 실패")
        
        return success
    
    # ==== 알람 설정 ====
    def set_alarm(self, warehouse: str, state: str) -> bool:
        """특정 창고의 알람 상태를 설정합니다."""
        # 창고 ID 유효성 확인
        if warehouse not in ["A", "B", "C", "D"]:
            logger.warning(f"알 수 없는 창고 ID: {warehouse}")
            return False
        
        # 창고에 따른 device ID 결정
        device_id = "hs_ab" if warehouse in ["A", "B"] else "hs_cd"
        
        # 상태 유효성 확인
        if state not in ["norm", "warn", "dang"]:
            logger.warning(f"알 수 없는 알람 상태: {state}")
            return False
        
        # 이미 같은 상태인지 확인 (불필요한 통신 방지)
        is_alarm_on = (state != "norm")
        if self.alarm_status[warehouse] == is_alarm_on:
            logger.debug(f"창고 {warehouse} 알람 상태가 이미 {state}입니다")
            return True
        
        # 명령 구성
        command = {
            "dev": device_id,
            "tp": "cmd",
            "cmd": "alr",
            "act": "set",
            "val": {
                warehouse: {
                    "st": state
                }
            }
        }
        
        # 명령 전송
        success = self.tcp_handler.send_message(device_id, command)
        
        if success:
            # 상태 업데이트
            self.alarm_status[warehouse] = is_alarm_on
            logger.debug(f"창고 {warehouse} 알람 설정 명령 전송 성공: 상태={state}")
        else:
            logger.error(f"창고 {warehouse} 알람 설정 명령 전송 실패")
        
        return success
    
    # ==== 제습기 설정 ====
    def set_dehumidifier(self, warehouse: str, on: bool) -> bool:
        """C, D 창고의 제습기를 켜거나 끕니다."""
        # 창고 ID 유효성 확인
        if warehouse not in ["C", "D"]:
            logger.warning(f"제습기 제어는 C, D 창고만 가능합니다: {warehouse}")
            return False
        
        # 명령 구성
        command = {
            "dev": "hs_cd",
            "tp": "cmd",
            "cmd": "deh",
            "act": "on" if on else "off",
            "val": {
                warehouse: on
            }
        }
        
        # 명령 전송
        success = self.tcp_handler.send_message("hs_cd", command)
        
        if success:
            logger.debug(f"창고 {warehouse} 제습기 설정 명령 전송 성공: {'켜기' if on else '끄기'}")
        else:
            logger.error(f"창고 {warehouse} 제습기 설정 명령 전송 실패")
        
        return success