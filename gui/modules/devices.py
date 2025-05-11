import sys
import requests
import json
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6 import QtUiTools

class DevicesPage(QWidget):
    def __init__(self, server_url="http://localhost:8000"):
        super().__init__()
        
        # UI 파일 로드
        loader = QtUiTools.QUiLoader()
        ui_file = QFile("ui/widgets/devices.ui")
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, None)  # 부모를 None으로 설정
        ui_file.close()
        
        # 레이아웃 설정
        layout = QVBoxLayout(self)
        layout.addWidget(self.ui)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # UI 요소 참조
        self.btn_start_sorting = self.ui.findChild(QPushButton, "btn_start_sorting")
        self.btn_stop_sorting = self.ui.findChild(QPushButton, "btn_stop_sorting")
        self.btn_emergency_stop = self.ui.findChild(QPushButton, "btn_emergency_stop")
        self.status_label = self.ui.findChild(QLabel, "status_label")
        self.status_value = self.ui.findChild(QLabel, "status_value")
        self.waiting_count = self.ui.findChild(QLabel, "waiting_count")
        self.processed_count = self.ui.findChild(QLabel, "processed_count")
        
        self.setWindowTitle("장치 제어")

        # 서버 URL 설정
        self.server_url = server_url
        
        # 버튼 이벤트 연결
        self.btn_start_sorting.clicked.connect(self.start_sorting)
        self.btn_stop_sorting.clicked.connect(self.stop_sorting)
        self.btn_emergency_stop.clicked.connect(self.emergency_stop)
        
        # 상태 업데이트 타이머
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(2000)  # 2초마다 업데이트
        
        # 초기 상태 업데이트
        self.update_status()
        
    def start_sorting(self):
        """분류 작업 시작"""
        try:
            response = requests.post(f"{self.server_url}/api/sort/start")
            if response.status_code == 200:
                data = response.json()
                self.status_label.setText(f"상태: {data.get('message', '분류 작업 시작')}")
                # 추가 상태 업데이트
                self.update_status()
            else:
                self.status_label.setText(f"오류: {response.status_code}")
        except Exception as e:
            self.status_label.setText(f"통신 오류: {str(e)}")
            
    def stop_sorting(self):
        """분류 작업 중지"""
        try:
            response = requests.post(f"{self.server_url}/api/sort/stop")
            if response.status_code == 200:
                data = response.json()
                self.status_label.setText(f"상태: {data.get('message', '분류 작업 중지')}")
                # 추가 상태 업데이트
                self.update_status()
            else:
                self.status_label.setText(f"오류: {response.status_code}")
        except Exception as e:
            self.status_label.setText(f"통신 오류: {str(e)}")
            
    def emergency_stop(self):
        """비상 정지"""
        try:
            response = requests.post(f"{self.server_url}/api/sort/emergency/stop")
            if response.status_code == 200:
                data = response.json()
                self.status_label.setText(f"상태: {data.get('message', '비상 정지')}")
                # 추가 상태 업데이트
                self.update_status()
            else:
                self.status_label.setText(f"오류: {response.status_code}")
        except Exception as e:
            self.status_label.setText(f"통신 오류: {str(e)}")
            
    def update_status(self):
        """상태 업데이트"""
        try:
            response = requests.get(f"{self.server_url}/api/sort/status")
            if response.status_code == 200:
                data = response.json()
                
                # 상태 업데이트
                current_status = data.get('current_status', 'unknown')
                self.status_value.setText(current_status)
                
                # 처리 수량 업데이트
                waiting_count = data.get('waiting_count', 0)
                processed_count = data.get('processed_count', 0)
                self.waiting_count.setText(str(waiting_count))
                self.processed_count.setText(str(processed_count))
                
                # 상태에 따른 스타일 설정
                if current_status == "running":
                    self.status_value.setStyleSheet("color: green; font-weight: bold;")
                elif current_status == "stopped":
                    self.status_value.setStyleSheet("color: orange; font-weight: bold;")
                elif current_status == "emergency":
                    self.status_value.setStyleSheet("color: red; font-weight: bold;")
            else:
                self.status_label.setText(f"상태 조회 오류: {response.status_code}")
        except Exception as e:
            # 통신 오류 - 로그만 출력하고 UI는 업데이트하지 않음
            print(f"상태 업데이트 오류: {str(e)}") 