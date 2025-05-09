import sys
from PyQt6 import QtWidgets, uic

class DashboardApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # UI 파일 로드
        uic.loadUi("dashboard.ui", self)  # UI 파일 이름과 경로가 일치해야 함

        # 초기값 설정이나 이벤트 연결도 여기서 가능
        self.setWindowTitle("풀필먼트 시스템 - 대시보드")
        self.show()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = DashboardApp()
    sys.exit(app.exec())
