import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6 import uic
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import koreanize_matplotlib

class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/widgets/dashboard.ui", self)
        self.setWindowTitle("물류 관리 시스템")        

        # 현재시간 표시 세팅
        self.current_datetime = QDateTime.currentDateTime()
        self.datetime.setText(self.current_datetime.toString("yyyy.MM.dd. hh:mm:ss"))

        # 현재 입출고 현황 표시 세팅        
        input_total = 120
        output_total = 100
        alert_total = 5
        self.total_status.setText(f"입고 {input_total}건  |  출고 {output_total}건  |  경고 {alert_total}건")
        self.total_status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 1초마다 현재시간, 입출고 현황 업데이트 되도록 연결
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time_and_status)
        self.timer.start(1000)

        # 입고량/출고량 그래프 생성
        self.createInventoryGraphs()

    # 현재시간, 입출고 현황 업데이트
    def update_time_and_status(self):
        self.current_datetime = QDateTime.currentDateTime()
        self.datetime.setText(self.current_datetime.toString("yyyy.MM.dd. hh:mm:ss"))

        input_total = 120
        output_total = 100
        alert_total = 5
        self.total_status.setText(f"입고 {input_total}건  |  출고 {output_total}건  |  경고 {alert_total}건")

    # 입출고 그래프 생성 메서드
    def createInventoryGraphs(self):
        # 데이터 준비
        days = ['1일', '5일', '10일', '15일', '20일', '25일', '30일']
        x = np.arange(len(days))
        in_data = [120, 140, 135, 150, 145, 160, 155]
        out_data = [100, 130, 125, 140, 135, 150, 145]
        
        # 입고량 그래프 생성
        self.createInputGraph(days, in_data)
        
        # 출고량 그래프 생성
        self.createOutputGraph(days, out_data)
        
        # 그래프 업데이트 타이머 (30분마다 업데이트)
        self.graph_timer = QTimer()
        self.graph_timer.timeout.connect(self.updateInventoryGraphs)
        self.graph_timer.start(30 * 60 * 1000)  # 30분 = 30 * 60 * 1000 ms
    
    # 입고량 그래프 생성
    def createInputGraph(self, days, data):
        # Figure 객체 생성
        self.input_figure = Figure(figsize=(5, 3), dpi=100)
        self.input_canvas = FigureCanvas(self.input_figure)
        
        # QWidget에 그래프 추가
        layout = QVBoxLayout(self.input_monthly_graph)
        layout.addWidget(self.input_canvas)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 그래프 설정
        self.input_ax = self.input_figure.add_subplot(111)
        self.input_ax.set_ylabel('수량', fontsize=9)    
        
        # 라인 그래프 그리기
        self.input_line, = self.input_ax.plot(days, data, '#4285F4', marker='o', linewidth=2, markersize=6)
        
        # x축 라벨 설정
        self.input_ax.set_xticks(range(len(days)))
        self.input_ax.set_xticklabels(days)
        self.input_ax.tick_params(axis='both', which='major', labelsize=8)            
        
        self.input_figure.tight_layout(pad=2)
        self.input_canvas.draw()
    
    # 출고량 그래프 생성
    def createOutputGraph(self, days, data):
        # Figure 객체 생성
        self.output_figure = Figure(figsize=(5, 3), dpi=100)
        self.output_canvas = FigureCanvas(self.output_figure)
        
        # QWidget에 그래프 추가
        layout = QVBoxLayout(self.output_monthly_graph)
        layout.addWidget(self.output_canvas)
        layout.setContentsMargins(0, 0, 0, 0)      
        
        # 그래프 설정
        self.output_ax = self.output_figure.add_subplot(111)
        self.output_ax.set_ylabel('수량', fontsize=9)
        
        # 그래프 그리기
        self.output_line, = self.output_ax.plot(days, data, '#4285F4', marker='o', linewidth=2, markersize=6)
        
        # x축 라벨 설정
        self.output_ax.set_xticks(range(len(days)))
        self.output_ax.set_xticklabels(days)
        self.output_ax.tick_params(axis='both', which='major', labelsize=8)  
                
        self.output_figure.tight_layout(pad=2)
        self.output_canvas.draw()
    
    # 그래프 업데이트 메서드
    def updateInventoryGraphs(self):
        # 실제로는 여기서 DB나 API에서 새 데이터를 가져옴
        # 예시 데이터
        days = ['1일', '5일', '10일', '15일', '20일', '25일', '30일']
        new_in_data = [110, 145, 130, 155, 140, 165, 160]
        new_out_data = [95, 135, 120, 145, 130, 155, 150]
        
        # 입고량 그래프 업데이트
        self.input_line.set_ydata(new_in_data)
        
        # y축 범위 업데이트
        self.input_ax.relim()
        self.input_ax.autoscale_view()
        
        # 데이터 포인트 값 업데이트
        for txt in self.input_ax.texts:
            txt.remove()
        
        # 캔버스 업데이트
        self.input_canvas.draw()
        
        # 출고량 그래프 업데이트
        self.output_line.set_ydata(new_out_data)
        
        # y축 범위 업데이트
        self.output_ax.relim()
        self.output_ax.autoscale_view()
        
        # 데이터 포인트 값 업데이트
        for txt in self.output_ax.texts:
            txt.remove()        
        
        # 캔버스 업데이트
        self.output_canvas.draw()
