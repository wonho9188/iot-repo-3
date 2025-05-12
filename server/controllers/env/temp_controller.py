# server/controllers/env/temp_controller.py
import logging
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

# ==== 온도 제어 클래스 ====
class TempController:
    # ==== 온도 제어 초기화 ====
    def __init__(self, tcp_handler):
        self.tcp_handler = tcp_handler
        
        # 지원되는 창고 목록
        self.warehouses = ["A", "B", "C"]
        
        # 창고별 알람 상태
        self.alarm_status = {
            "A": False,
            "B": False,
            "C": False
        }
        
        # 창고별 온도 범위
        self.temp_ranges = {
            "A": (-30, -18),  # 냉동
            "B": (0, 10),     # 냉장
            "C": (15, 25)     # 상온
        }
        
        logger.info("온도 제어 모듈 초기화 완료")
    
    # ==== 온도 범위 반환 ====
    def get_temperature_range(self, warehouse: str) -> Tuple[int, int]:

        if warehouse in self.temp_ranges:
            return self.temp_ranges[warehouse]
        return (0, 0)  # 기본값
    
    # ==== 팬 제어 명령 전송 ====
    def set_fan(self, warehouse: str, mode: str, speed: int) -> bool:
        """특정 창고의 팬 모드와 속도를 설정합니다."""
        # 창고 ID 유효성 확인
        if warehouse not in self.warehouses:
            logger.warning(f"알 수 없는 창고 ID: {warehouse}")
            return False
        
        # 모드 유효성 확인
        if mode not in ["cool", "heat", "off"]:
            logger.warning(f"알 수 없는 팬 모드: {mode}")
            return False
        
        # 속도 유효성 확인
        if not (0 <= speed <= 3):
            logger.warning(f"유효하지 않은 팬 속도: {speed}")
            return False
        
        # 명령 생성 - 바이너리 프로토콜 형식
        # HCfA2\n - 하우스(H) 명령(C) 팬(f) A창고(A) 속도2(2)
        command = f"HCf{warehouse}{speed}\n"
        
        # 명령 전송
        success = self.tcp_handler.send_message("H", command)
        
        if success:
            logger.debug(f"창고 {warehouse} 팬 설정 명령 전송 성공: 모드={mode}, 속도={speed}")
        else:
            logger.error(f"창고 {warehouse} 팬 설정 명령 전송 실패")
        
        return success
    
    # ==== 알람 설정 ====
    def set_alarm(self, warehouse: str, state: str) -> bool:
        """특정 창고의 알람 상태를 설정합니다."""
        # 창고 ID 유효성 확인
        if warehouse not in self.warehouses:
            logger.warning(f"알 수 없는 창고 ID: {warehouse}")
            return False
        
        # 상태 유효성 확인
        if state not in ["norm", "warn", "dang"]:
            logger.warning(f"알 수 없는 알람 상태: {state}")
            return False
        
        # 이미 같은 상태인지 확인 (불필요한 통신 방지)
        is_alarm_on = (state != "norm")
        if self.alarm_status[warehouse] == is_alarm_on:
            logger.debug(f"창고 {warehouse} 알람 상태: {state}")
            return True
        
        # 명령 생성 - 바이너리 프로토콜 형식
        # HCaA1\n - 하우스(H) 명령(C) 알람(a) A창고(A) 상태1-켜기(1) 또는 0-끄기(0)
        command = f"HCa{warehouse}{1 if is_alarm_on else 0}\n"
        
        # 명령 전송
        success = self.tcp_handler.send_message("H", command)
        
        if success:
            # 상태 업데이트
            self.alarm_status[warehouse] = is_alarm_on
            logger.debug(f"창고 {warehouse} 알람 설정 명령 전송 성공: 상태={state}")
        else:
            logger.error(f"창고 {warehouse} 알람 설정 명령 전송 실패")
        
        return success
    
    # ==== 목표 온도 설정 ====
    def set_target_temperature(self, warehouse: str, temp: float) -> bool:
        """특정 창고의 목표 온도를 내부 상태에 설정합니다."""
        if warehouse not in self.warehouses:
            logger.warning(f"알 수 없는 창고 ID: {warehouse}")
            return False
            
        # 내부 처리만 하는 메서드
        logger.debug(f"창고 {warehouse} 목표 온도 설정: {temp}°C")
        return True