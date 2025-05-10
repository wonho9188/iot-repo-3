

# 네트워크 설정
SERVER_IP = "192.168.0.10"  # 서버 IP
TCP_PORT = 9000             # TCP 소켓 포트
API_PORT = 8000             # FastAPI 포트

# DB 설정 (간단한 설정)
DB_HOST = "localhost"
DB_USER = "root"
DB_PASS = "password"
DB_NAME = "fulfillment"

# 창고 환경 임계값
WAREHOUSE_TEMP = {
    "A": {"min": -30, "max": -18},  # 냉동고
    "B": {"min": 0, "max": 10},     # 냉장고
    "C": {"min": 15, "max": 25},    # 상온
    "D": {"min": 15, "max": 25}     # 비식품
}

WAREHOUSE_HUMIDITY = {
    "C": {"min": 20, "max": 60},  # 상온 습도
    "D": {"min": 20, "max": 60}   # 비식품 습도
}

# 시간 관련 설정
AUTO_STOP_TIMEOUT = 10  # 10초 동안 물품 미감지 시 자동 정지
ACCESS_SERVO_TIMEOUT = 2  # 출입문 열림 상태 유지 시간(초)

# 메모리 DB (단순화를 위한 임시 저장소)
# 프로토타입에서는 실제 DB 연결 대신 메모리에 데이터 저장
MEMORY_DB = {
    "inventory": [],  # 재고 아이템 목록
    "environment": {  # 환경 데이터
        "A": {"temp": -20, "humidity": 0, "status": "normal"},
        "B": {"temp": 5, "humidity": 0, "status": "normal"},
        "C": {"temp": 22, "humidity": 45, "status": "normal"},
        "D": {"temp": 22, "humidity": 40, "status": "normal"},
    },
    "access_logs": [],  # 출입 기록
    "employees": [  # 직원 정보 (출입 권한용)
        {"id": "E39368F5", "name": "김민준", "department": "물류팀", "access": True},
        {"id": "E47291A3", "name": "이서연", "department": "품질관리팀", "access": True},
        {"id": "E58213F7", "name": "박지훈", "department": "외부인", "access": False},
    ]
}