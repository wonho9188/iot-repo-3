import json
import logging
from enum import Enum
from typing import Dict, Optional
from datetime import datetime

class EnvironmentStatus(Enum):
    """환경 상태 열거형"""
    NORMAL = "normal"    # 정상
    WARNING = "warning"  # 경고
    DANGER = "danger"    # 위험

class FanMode(Enum):
    """팬 모드 열거형"""
    COOL = "cool"    # 냉방
    HEAT = "heat"    # 난방
    OFF = "off"      # 정지

class EnvironmentController:
    """환경 제어 컨트롤러 클래스
    
    창고 환경(온도) 제어 시스템의 비즈니스 로직을 처리하는 클래스입니다.
    온도 모니터링, 팬 제어, 경고 상태 관리 등의 기능을 제공합니다.
    """
    
    def __init__(self, tcp_handler, websocket_manager, db_helper=None):
        """환경 제어 컨트롤러 초기화
        
        Args:
            tcp_handler: TCP 통신 핸들러
            websocket_manager: WebSocket 통신 관리자
            db_helper: 데이터베이스 헬퍼
        """
        self.tcp_handler = tcp_handler
        self.ws_manager = websocket_manager
        self.db = db_helper
        self.logger = logging.getLogger(__name__)
        
        # 창고별 환경 데이터
        self.environment_data = {
            'A': {'temp': -20, 'humidity': 0, 'status': EnvironmentStatus.NORMAL},
            'B': {'temp': 5, 'humidity': 0, 'status': EnvironmentStatus.NORMAL},
            'C': {'temp': 22, 'humidity': 45, 'status': EnvironmentStatus.NORMAL},
            'D': {'temp': 22, 'humidity': 40, 'status': EnvironmentStatus.NORMAL}
        }
        
        # 창고별 온도 범위 설정
        self.temp_ranges = {
            'A': {'min': -30, 'max': -18},  # 냉동
            'B': {'min': 0, 'max': 10},     # 냉장
            'C': {'min': 15, 'max': 25},    # 상온
            'D': {'min': 15, 'max': 25}     # 비식품
        }
        
    def handle_message(self, message: Dict):
        """TCP 메시지를 처리합니다.
        
        Args:
            message (Dict): 수신된 메시지
        """
        try:
            if message.get('tp') == 'evt' and message.get('evt') == 'tmp':
                # 온도 측정 이벤트 처리
                self.process_temperature(message.get('val', {}))
            elif message.get('tp') == 'res':
                # 응답 메시지 처리
                self.handle_response(message)
                
        except Exception as e:
            self.logger.error(f"메시지 처리 중 오류 발생: {str(e)}")
            
    def process_temperature(self, temp_data: Dict):
        """온도 데이터를 처리하고 팬을 제어합니다.
        
        Args:
            temp_data (Dict): 온도 데이터
        """
        try:
            for warehouse_id, data in temp_data.items():
                if warehouse_id not in self.environment_data:
                    continue
                    
                current_temp = data.get('t')
                if current_temp is None:
                    continue
                    
                # 이전 상태 저장
                prev_status = self.environment_data[warehouse_id]['status']
                
                # 온도 범위 확인 및 상태 결정
                temp_range = self.temp_ranges[warehouse_id]
                status = self.check_thresholds(current_temp, temp_range)
                
                # 상태가 변경된 경우에만 처리
                if status != prev_status:
                    self.environment_data[warehouse_id]['status'] = status
                    self.environment_data[warehouse_id]['temp'] = current_temp
                    
                    # 이상치 로그 기록
                    if self.db:
                        self.db.log_environment_anomaly({
                            'warehouse_id': warehouse_id,
                            'temperature': current_temp,
                            'status': status.value,
                            'timestamp': datetime.now().isoformat()
                        })
                    
                    # GUI 업데이트
                    self.update_gui()
                    
                # 팬 제어
                self.control_fan(warehouse_id, current_temp, temp_range)
                
        except Exception as e:
            self.logger.error(f"온도 처리 중 오류 발생: {str(e)}")
            
    def check_thresholds(self, temperature: float, temp_range: Dict) -> EnvironmentStatus:
        """온도 임계값을 확인하고 상태를 결정합니다.
        
        Args:
            temperature (float): 현재 온도
            temp_range (Dict): 온도 범위 설정
            
        Returns:
            EnvironmentStatus: 결정된 상태
        """
        min_temp = temp_range['min']
        max_temp = temp_range['max']
        
        if temperature < min_temp - 8 or temperature > max_temp + 8:
            return EnvironmentStatus.DANGER
        elif temperature < min_temp - 4 or temperature > max_temp + 4:
            return EnvironmentStatus.WARNING
        else:
            return EnvironmentStatus.NORMAL
            
    def control_fan(self, warehouse_id: str, current_temp: float, temp_range: Dict):
        """팬을 제어합니다.
        
        Args:
            warehouse_id (str): 창고 ID
            current_temp (float): 현재 온도
            temp_range (Dict): 온도 범위 설정
        """
        try:
            target_temp = (temp_range['min'] + temp_range['max']) / 2
            temp_diff = current_temp - target_temp
            
            # 팬 모드 및 속도 결정
            if abs(temp_diff) < 1:
                mode = FanMode.OFF
                speed = 0
            else:
                mode = FanMode.COOL if temp_diff > 0 else FanMode.HEAT
                speed = min(3, int(abs(temp_diff) / 2) + 1)
                
            # 팬 제어 명령 전송
            message = {
                "dev": "hs",
                "tp": "cmd",
                "cmd": "fan",
                "act": "set",
                "val": {
                    "wh": warehouse_id,
                    "md": mode.value,
                    "sp": speed
                }
            }
            self.tcp_handler.send_message("hs", message)
            
        except Exception as e:
            self.logger.error(f"팬 제어 중 오류 발생: {str(e)}")
            
    def handle_response(self, response_data: Dict):
        """응답 메시지를 처리합니다.
        
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
            
    def update_gui(self):
        """GUI를 업데이트합니다."""
        status_data = {
            "type": "environment_status",
            "data": {
                warehouse_id: {
                    "temperature": data['temp'],
                    "humidity": data['humidity'],
                    "status": data['status'].value
                }
                for warehouse_id, data in self.environment_data.items()
            }
        }
        
        # WebSocket으로 상태 브로드캐스트
        self.ws_manager.broadcast("environment_status", status_data)
        
    def get_environment_status(self) -> Dict:
        """현재 환경 상태를 반환합니다.
        
        Returns:
            Dict: 현재 환경 상태
        """
        return {
            warehouse_id: {
                "temperature": data['temp'],
                "humidity": data['humidity'],
                "status": data['status'].value
            }
            for warehouse_id, data in self.environment_data.items()
        }
        
    def set_temperature(self, warehouse_id: str, temperature: float) -> bool:
        """목표 온도를 설정합니다.
        
        Args:
            warehouse_id (str): 창고 ID
            temperature (float): 목표 온도
            
        Returns:
            bool: 설정 성공 여부
        """
        if warehouse_id not in self.temp_ranges:
            self.logger.error(f"잘못된 창고 ID: {warehouse_id}")
            return False
            
        # 온도 범위 검증
        min_temp = self.temp_ranges[warehouse_id]['min']
        max_temp = self.temp_ranges[warehouse_id]['max']
        
        if temperature < min_temp or temperature > max_temp:
            self.logger.error(f"온도가 허용 범위를 벗어남: {temperature}")
            return False
            
        # 온도 설정 명령 전송
        message = {
            "dev": "hs",
            "tp": "cmd",
            "cmd": "temp",
            "act": "set",
            "val": {
                "wh": warehouse_id,
                "t": temperature
            }
        }
        success = self.tcp_handler.send_message("hs", message)
        
        if success:
            self.logger.info(f"온도 설정: {warehouse_id} -> {temperature}°C")
            return True
        else:
            self.logger.error("온도 설정 명령 전송 실패")
            return False
            
    def get_temperature_history(self, warehouse_id: str, hours: int = 24) -> list:
        """온도 이력을 조회합니다.
        
        Args:
            warehouse_id (str): 창고 ID
            hours (int): 조회 시간 범위 (시간)
            
        Returns:
            list: 온도 이력 데이터
        """
        # 더미 데이터 반환 (DB 연동 시 실제 데이터로 대체)
        return [
            {
                "timestamp": datetime.now().isoformat(),
                "temperature": self.environment_data[warehouse_id]['temp'],
                "status": self.environment_data[warehouse_id]['status'].value
            }
        ]
