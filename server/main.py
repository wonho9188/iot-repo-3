from flask import Flask, jsonify, request   # 웹 서버와 요청/응답
from flask_cors import CORS                 # 크로스 도메인 허용 (CORS)
from utils.logging import setup_logger      # utils/로깅 전용파일
from flask_socketio import SocketIO        
from api.sort_api import bp as sort_bp      # api 파일들 
from api.inventory_api import bp as inventory_bp
from api.env_api import bp as env_bp
from api.access_api import bp as access_bp
from api.expiry_api import bp as expiry_bp
from controllers.system_controller import get_system_status 
from controllers.sort_controller import SortController
from utils.tcp_handler import TCPHandler

# TCP 핸들러 초기화
tcp_handler = TCPHandler(SERVER_HOST, TCP_PORT)

# 분류기 컨트롤러 초기화
sort_controller = SortController(tcp_handler, socketio)

app = Flask(__name__)      # Flask 앱 객체를 생성
CORS(app)                  # GUI에서 API 호출 허용
socketio = SocketIO(app, cors_allowed_origins="*")  # Socket.IO 초기화

logger = setup_logger("server")     # utils/logging.py 사용용
logger.info("==== 서버 시작 ====")

# ==== 기능별로 분리된 API 모듈을 임포트 ====
app.register_blueprint(sort_bp, url_prefix='/api')
app.register_blueprint(inventory_bp, url_prefix='/api')
app.register_blueprint(env_bp, url_prefix='/api')
app.register_blueprint(access_api, url_prefix='/api')
app.register_blueprint(expiry_bp, url_prefix='/api')

# ==== 해당 요청 시 get_system_status 함수를 호출하여 시스템 상태를 반환 ====
@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify(get_system_status())

# ==== HTTP 오류 코드(404, 500)에 대한 처리함수 등록 ====
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"status": "error", "message": "리소스를 찾을 수 없습니다"}), 404
@app.errorhandler(500)
def internal_error(error):
    app.logger.error('서버 오류: %s', str(error))
    return jsonify({"status": "error", "message": "서버 내부 오류가 발생했습니다"}), 500

# ==== 서버 실행 ====
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True) #  서버가 리스닝할 TCP 포트를 지정