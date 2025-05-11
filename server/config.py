# ===== 풀필먼트 시스템 설정 파일 =====
# ===== 시스템의 모든 설정을 중앙화하여 관리 =====
import os
from typing import Dict, Any
from pathlib import Path

# 기본 경로 설정
BASE_DIR = Path(__file__).resolve().parent.parent

# .env 파일 로드 (있는 경우)
try:
    from dotenv import load_dotenv
    ENV_PATH = BASE_DIR / '.env'
    if ENV_PATH.exists():
        load_dotenv(dotenv_path=ENV_PATH)
except ImportError:
    pass     # python-dotenv가 설치되지 않은 경우 무시

# ===== 서버 설정 =====
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# ===== 데이터베이스 설정 =====
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_NAME = os.getenv("DB_NAME", "rail_automation")
DB_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# ===== TCP 하드웨어 통신 설정 =====
TCP_PORT = int(os.getenv("TCP_PORT", "9000"))
HARDWARE_IP = {
    'sort_controller': os.getenv("SORT_CONTROLLER_IP", '192.168.0.101'),
    'env_controller_ab': os.getenv("ENV_AB_CONTROLLER_IP", '192.168.0.102'),
    'env_controller_cd': os.getenv("ENV_CD_CONTROLLER_IP", '192.168.0.103'),
    'access_controller': os.getenv("ACCESS_CONTROLLER_IP", '192.168.0.104')
}

# ===== Socket.IO 설정 =====
SOCKETIO_PING_TIMEOUT = int(os.getenv("SOCKETIO_PING_TIMEOUT", "5"))
SOCKETIO_PING_INTERVAL = int(os.getenv("SOCKETIO_PING_INTERVAL", "25"))
SOCKETIO_ASYNC_MODE = os.getenv("SOCKETIO_ASYNC_MODE", "threading") 

# ===== 창고 환경 설정 =====
WAREHOUSES = {
    # A: 냉동 식품 창고 (-30°C ~ -18°C)
    "A": {"type": "freezer", "temp_min": -30, "temp_max": -18},
    # B: 냉장 식품 창고 (0°C ~ 10°C)
    "B": {"type": "refrigerator", "temp_min": 0, "temp_max": 10},
    # C: 상온 식품 창고 (15°C ~ 25°C)
    "C": {"type": "room_temp", "temp_min": 15, "temp_max": 25},
    # D: 비식품 창고 (15°C ~ 25°C)
    "D": {"type": "ambient", "temp_min": 15, "temp_max": 25}
}

# ===== 로깅 설정 =====
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "server.log")
LOG_MAX_SIZE = int(os.getenv("LOG_MAX_SIZE", str(10 * 1024 * 1024)))  # 10MB
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "5"))

# ===== 시스템 모니터링 설정 =====
STATUS_CHECK_INTERVAL = int(os.getenv("STATUS_CHECK_INTERVAL", "10"))  # 상태 점검 주기(10초)