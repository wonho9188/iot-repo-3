from flask import Flask, jsonify, request
from flask_cors import CORS
from utils.logging import setup_logger
from flask_socketio import SocketIO
from config import SERVER_HOST, SERVER_PORT, TCP_PORT, DEBUG, SOCKETIO_PING_TIMEOUT, SOCKETIO_PING_INTERVAL, SOCKETIO_ASYNC_MODE  # socketio 설정 추가
from api.sort_api import bp as sort_bp
from api.inventory_api import bp as inventory_bp
from api.env_api import bp as env_bp
from api.access_api import bp as access_bp
from api.expiry_api import bp as expiry_bp
from controllers.system_controller import get_system_status
from controllers.sort.sort_controller import SortController
from utils.tcp_handler import TCPHandler
from api import set_controller  # API 컨트롤러 설정 함수 임포트

# logger 초기화 전에 로그 디렉토리 확인
import os
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

logger = setup_logger("server")
app = Flask(__name__)
CORS(app)

# socketio 설정 개선
socketio = SocketIO(
    app, 
    cors_allowed_origins="*", 
    ping_timeout=SOCKETIO_PING_TIMEOUT,
    ping_interval=SOCKETIO_PING_INTERVAL,
    async_mode=SOCKETIO_ASYNC_MODE
)

# TCP 핸들러 초기화 및 시작
tcp_handler = TCPHandler(SERVER_HOST, TCP_PORT)
tcp_handler.start()  # TCP 서버 시작 호출 추가

# 분류기 컨트롤러 초기화
sort_controller = SortController(tcp_handler, socketio)

# API 컨트롤러 설정
set_controller(sort_controller)  # API에 컨트롤러 등록

logger = setup_logger("server")
logger.info("==== 서버 시작 ====")

# 기능별로 분리된 API 모듈을 등록
app.register_blueprint(sort_bp, url_prefix='/api')
app.register_blueprint(inventory_bp, url_prefix='/api')
app.register_blueprint(env_bp, url_prefix='/api')
app.register_blueprint(access_bp, url_prefix='/api')
app.register_blueprint(expiry_bp, url_prefix='/api')

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify(get_system_status())

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"status": "error", "message": "리소스를 찾을 수 없습니다"}), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error('서버 오류: %s', str(error))
    return jsonify({"status": "error", "message": "서버 내부 오류가 발생했습니다"}), 500

# 종료 함수 추가
def shutdown():
    """서버 종료 시 정리 작업"""
    tcp_handler.stop()
    logger.info("==== 서버 종료 ====")

if __name__ == '__main__':
    try:
        socketio.run(app, host=SERVER_HOST, port=SERVER_PORT, debug=DEBUG)
    finally:
        shutdown()  # 서버 종료 시 정리 작업 수행