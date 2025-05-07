# ===== 스마트 창고 관리 시스템 설정 파일 =====
# ===== 시스템의 모든 설정을 중앙화하여 관리 =====
import os
from typing import Dict, Any
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent   # 프로젝트 루트 경로 찾기
ENV_PATH = BASE_DIR / '.env'
load_dotenv(dotenv_path=ENV_PATH)                   # .env 파일 로드


# ===== 기본 설정 =====
CONFIG: Dict[str, Any] = {

    "HOST": os.getenv("SERVER_HOST", "0.0.0.0"),    # 서버 설정
    "PORT": int(os.getenv("SERVER_PORT", "8000")),  # PORT: 서버가 사용할 포트 번호

    "DB_HOST": os.getenv("DB_HOST", "localhost"),   # 데이터베이스 서버의 호스트명 또는 IP 주소
    "DB_PORT": int(os.getenv("DB_PORT", "3306")),   # 데이터베이스 서버의 포트 번호
    "DB_USER": os.getenv("DB_USER", "warehouse_user"),  # 데이터베이스 접속 사용자 이름
    "DB_PASSWORD": os.getenv("DB_PASSWORD", "warehouse_password"),  # 데이터베이스 접속 비밀번호
    "DB_NAME": os.getenv("DB_NAME", "smart_warehouse"), # 사용할 데이터베이스 이름

    "MQTT_BROKER": os.getenv("MQTT_BROKER", "localhost"),   # MQTT 브로커 호스트명 또는 IP 주소
    "MQTT_PORT": int(os.getenv("MQTT_PORT", "1883")),   # MQTT 브로커 포트 번호. 기본 포트는 1883
    "MQTT_CLIENT_ID": os.getenv("MQTT_CLIENT_ID", "server"),    # 서버의 MQTT 클라이언트 고유한 ID
    
    "TOPIC_PREFIX": "v1/",             # TOPIC_PREFIX: 모든 MQTT 토픽의 접두사
    
    # ===== 각 창고의 온도/습도 범위 및 유형 정의 =====
    "WAREHOUSES": {
        # A: 냉동 식품 창고 (-30°C ~ -18°C, 습도 95% 이상)
        "A": {"type": "freezer", "temp_min": -30, "temp_max": -18, "hum_min": 95, "hum_max": 100},
        # B: 냉장 식품 창고 (0°C ~ 10°C, 습도 90% 이상)
        "B": {"type": "refrigerator", "temp_min": 0, "temp_max": 10, "hum_min": 90, "hum_max": 100},
        # C: 상온 식품 창고 (15°C ~ 25°C, 습도 50~60%)
        "C": {"type": "room_temp", "temp_min": 15, "temp_max": 25, "hum_min": 50, "hum_max": 60},
        # D: 실온 물품 창고 (1°C ~ 35°C, 습도 50~60%)
        "D": {"type": "ambient", "temp_min": 1, "temp_max": 35, "hum_min": 50, "hum_max": 60}
    },
    
    "JWT_SECRET": os.getenv("JWT_SECRET", "your-secret-key"),   # 토큰 서명에 사용되는 비밀 키
    "JWT_ALGORITHM": "HS256",       # 토큰 서명에 사용되는 알고리즘(HS256은 HMAC + SHA256)
    "JWT_EXPIRATION": 60 * 24,      # 토큰 만료 시간(분), 기본 24시간간
    
    # ===== 시스템의 작동 상태, 오류, 경고 등을 기록하는 기능 =====
    "LOGGING": {
        "LEVEL": os.getenv("LOG_LEVEL", "INFO"),        # 로깅 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        "FILE": os.getenv("LOG_FILE", "server.log"),    # 로그 파일 경로
        "MAX_SIZE": 10 * 1024 * 1024,       # 로그 파일 최대 크기(바이트), 기본 10MB
        "BACKUP_COUNT": 5                   # 보관할 이전 로그 파일 수
    },
    # 모니터링 설정
    "MONITORING": {
        "TEMP_CHECK_INTERVAL": int(os.getenv("TEMP_CHECK_INTERVAL", "300")),     # 온도 체크 주기(초), 기본 5분
        "EXPIRY_CHECK_INTERVAL": int(os.getenv("EXPIRY_CHECK_INTERVAL", "3600")) # 유통기한 체크 주기(초), 기본 1시간
    }
}

# 데이터베이스 URL 생성
CONFIG["DB_URL"] = f"mysql+pymysql://{CONFIG['DB_USER']}:{CONFIG['DB_PASSWORD']}@{CONFIG['DB_HOST']}:{CONFIG['DB_PORT']}/{CONFIG['DB_NAME']}"