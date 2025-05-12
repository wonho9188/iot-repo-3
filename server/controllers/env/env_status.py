from enum import Enum
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# ==== 환경 상태 열거형 ====
class EnvState(Enum):
    NORMAL = "normal"      # 정상 상태
    WARNING = "warning"    # 경고 상태 (설정 범위 초과)
    DANGER = "danger"      # 위험 상태 (설정 범위 크게 초과)

# ==== 팬 모드 열거형 ====
class FanMode(Enum):
    OFF = "off"        # 정지
    COOLING = "cool"   # 냉방
    HEATING = "heat"   # 난방

# ==== 환경 상태 관리 클래스 ====
class EnvStatus:
    # ==== 환경 상태 관리자 초기화 ====
    def __init__(self, controller):
        self.controller = controller
        
        # 창고별 현재 측정 온도 (ESP32 온도 센서에서 받는 값)
        self.warehouse_temps = {
            "A": None,  # 냉동
            "B": None,  # 냉장
            "C": None   # 상온
        }
        
        # 창고별 목표 온도 설정 (사용자가 UI에서 설정하는 값)
        self.target_temps = {
            "A": -20.0,  # 냉동 창고 목표 온도 기본값
            "B": 4.0,    # 냉장 창고 목표 온도 기본값
            "C": 20.0    # 상온 창고 목표 온도 기본값
        }
        
        # 창고별 팬 상태
        self.fan_status = {
            "A": {"mode": FanMode.COOLING, "speed": 1},
            "B": {"mode": FanMode.COOLING, "speed": 1},
            "C": {"mode": FanMode.OFF, "speed": 0}
        }
        
        # 창고별 환경 상태
        self.env_states = {
            "A": EnvState.NORMAL,
            "B": EnvState.NORMAL,
            "C": EnvState.NORMAL
        }
        
        # 온도 범위 설정
        self.temp_ranges = {
            "A": {"min": -25, "max": -18},  # 냉동
            "B": {"min": 0, "max": 10},     # 냉장
            "C": {"min": 15, "max": 25}     # 상온
        }
        
        logger.info("환경 상태 관리자 초기화 완료")
    
    # ==== 온도 데이터 업데이트 ====
    def update_temperature(self, warehouse: str, temp: float) -> Dict:
        """특정 창고의 온도 데이터를 업데이트하고 상태를 반환합니다."""
        if warehouse not in self.warehouse_temps:
            logger.warning(f"알 수 없는 창고 ID: {warehouse}")
            return {}
        
        prev_temp = self.warehouse_temps[warehouse]
        self.warehouse_temps[warehouse] = temp
        
        # 상태 업데이트
        prev_state = self.env_states[warehouse]
        self._update_state(warehouse)
        
        # 팬 제어 모드 및 속도 결정
        self._determine_fan_mode(warehouse)
        
        # 결과 반환
        result = {
            "warehouse": warehouse,
            "temp": temp,
            "state": self.env_states[warehouse].value,
            "fan_mode": self.fan_status[warehouse]["mode"].value,
            "fan_speed": self.fan_status[warehouse]["speed"]
        }
        
        # 온도 또는 상태가 변경된 경우 로그 기록
        if prev_temp != temp or prev_state != self.env_states[warehouse]:
            logger.info(f"창고 {warehouse} 온도 변경: {prev_temp} → {temp}, " + 
                        f"상태: {prev_state.value if prev_state else 'None'} → {self.env_states[warehouse].value}")
        
        return result
    
    # ==== 상태 평가 및 업데이트 ====
    def _update_state(self, warehouse: str):
        """온도에 따른 환경 상태를 업데이트합니다."""
        temp = self.warehouse_temps[warehouse]
        
        if temp is None:
            return
        
        # 온도 범위 가져오기
        temp_range = self.temp_ranges[warehouse]
        
        # 온도에 따른 상태 결정
        if temp_range["min"] <= temp <= temp_range["max"]:
            # 정상 범위
            self.env_states[warehouse] = EnvState.NORMAL
        elif (temp_range["min"] - 4 <= temp < temp_range["min"]) or (temp_range["max"] < temp <= temp_range["max"] + 4):
            # 경고 범위 (±4도)
            self.env_states[warehouse] = EnvState.WARNING
        else:
            # 위험 범위 (±4도 초과)
            self.env_states[warehouse] = EnvState.DANGER
    
    # ==== 팬 모드 및 속도 결정 ====
    def _determine_fan_mode(self, warehouse: str):
        """온도에 따른 팬 모드 및 속도를 결정합니다."""
        temp = self.warehouse_temps[warehouse]
        target = self.target_temps[warehouse]
        
        if temp is None:
            return
        
        # 창고별 팬 모드 결정 로직
        if warehouse in ["A", "B"]:  # 냉동/냉장
            # 기본적으로 항상 작동
            if temp > target:
                # 온도가 목표보다 높으면 냉방
                self.fan_status[warehouse]["mode"] = FanMode.COOLING
                # 편차에 따른 팬 속도 결정
                diff = temp - target
                if diff <= 2:
                    self.fan_status[warehouse]["speed"] = 1
                elif diff <= 6:
                    self.fan_status[warehouse]["speed"] = 2
                else:
                    self.fan_status[warehouse]["speed"] = 3
            else:
                # 온도가 목표보다 낮으면 난방
                self.fan_status[warehouse]["mode"] = FanMode.HEATING
                # 편차에 따른 팬 속도 결정
                diff = target - temp
                if diff <= 2:
                    self.fan_status[warehouse]["speed"] = 1
                elif diff <= 6:
                    self.fan_status[warehouse]["speed"] = 2
                else:
                    self.fan_status[warehouse]["speed"] = 3
        else:  # C (상온)
            # 온도가 범위 내이면 정지
            if self.temp_ranges[warehouse]["min"] <= temp <= self.temp_ranges[warehouse]["max"]:
                self.fan_status[warehouse]["mode"] = FanMode.OFF
                self.fan_status[warehouse]["speed"] = 0
            elif temp < self.temp_ranges[warehouse]["min"]:
                # 온도가 범위보다 낮으면 난방
                self.fan_status[warehouse]["mode"] = FanMode.HEATING
                # 편차에 따른 팬 속도 결정
                diff = self.temp_ranges[warehouse]["min"] - temp
                if diff <= 2:
                    self.fan_status[warehouse]["speed"] = 1
                elif diff <= 6:
                    self.fan_status[warehouse]["speed"] = 2
                else:
                    self.fan_status[warehouse]["speed"] = 3
            else:
                # 온도가 범위보다 높으면 냉방
                self.fan_status[warehouse]["mode"] = FanMode.COOLING
                # 편차에 따른 팬 속도 결정
                diff = temp - self.temp_ranges[warehouse]["max"]
                if diff <= 2:
                    self.fan_status[warehouse]["speed"] = 1
                elif diff <= 6:
                    self.fan_status[warehouse]["speed"] = 2
                else:
                    self.fan_status[warehouse]["speed"] = 3
    
    # ==== 목표 온도 설정 ====
    def set_target_temperature(self, warehouse: str, temp: float) -> Dict:
        """특정 창고의 목표 온도를 설정합니다."""
        if warehouse not in self.target_temps:
            logger.warning(f"알 수 없는 창고 ID: {warehouse}")
            return {}
        
        # 유효한 범위 내인지 확인
        if not (self.temp_ranges[warehouse]["min"] - 5 <= temp <= self.temp_ranges[warehouse]["max"] + 5):
            logger.warning(f"창고 {warehouse}의 목표 온도가 유효 범위를 벗어남: {temp}")
            return {}
        
        # 목표 온도 업데이트
        prev_target = self.target_temps[warehouse]
        self.target_temps[warehouse] = temp
        
        # 팬 모드 재계산
        self._determine_fan_mode(warehouse)
        
        logger.info(f"창고 {warehouse} 목표 온도 변경: {prev_target} → {temp}")
        
        # 결과 반환
        return {
            "warehouse": warehouse,
            "target_temp": temp,
            "fan_mode": self.fan_status[warehouse]["mode"].value,
            "fan_speed": self.fan_status[warehouse]["speed"]
        }
    
    # ==== 현재 상태 정보 반환 ====
    def get_status_data(self) -> Dict[str, Any]:
        """모든 창고의 현재 환경 상태 정보를 반환합니다."""
        warehouses = {}
        
        for wh in ["A", "B", "C"]:
            warehouses[wh] = {
                "temp": self.warehouse_temps[wh],
                "target_temp": self.target_temps[wh],
                "status": self.env_states[wh].value if self.env_states[wh] else None,
                "fan_mode": self.fan_status[wh]["mode"].value,
                "fan_speed": self.fan_status[wh]["speed"]
            }
        
        return {
            "warehouses": warehouses
        }