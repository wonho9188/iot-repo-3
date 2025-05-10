# iot-repo-3

## 폴더 별 역할
```

📁 docs : 설명 문서
ㄴ CODE_STANDARD.md : 코딩 스탠다드
ㄴ .env   : 시스템의 모든 설정을 중앙화
ㄴ config.py  : 애플리케이션 설정값(환경 변수, 상수 등)을 저장

📁 firmware : C++ 기반 아두이노 관리 폴더 (ino 확장자)
ㄴ config.h                 : 핀 번호, MQTT 토픽, 상수 등 공통 설정 정의
ㄴ main.ino                 : 진입점. setup()과 loop()만 존재하며 직접 로직 없음
ㄴ 📁 modules               : 센서 및 액추에이터별 기능 구현 파일
   ㄴ barcode.ino           : 바코드 스캐너 제어 및 MQTT 전송
   ㄴ ir_sensor.ino         : 분류대 IR 센서 감지 처리
   ㄴ dc_motor.ino          : 컨베이어용 DC 모터 제어
   ㄴ temp_humidity.ino     : 온도/습도 센서 측정 및 전송
   ㄴ fan.ino               : 창고 팬 작동 및 자동 제어
   ㄴ rfid.ino              : 출입관리용 RFID 리더기 처리
ㄴ 📁 communication         : MQTT 통신 관련 공통 코드
   ㄴ mqtt_util.ino         : MQTT 연결, publish(), reconnect 등 처리
   ㄴ packet_helper.ino     : JSON 포맷 구성, 토픽 문자열 생성 등 유틸 함수
ㄴ 📁 include               : 공통 헤더 파일 정의
   ㄴ sensors.h             : 각 센서별 init_함수, read_함수 선언용 헤더

📁 server/
├── main.py              # 서버 진입점 (FastAPI + TCP 소켓 서버)
├── config.py            # 설정 (IP, 포트, 상수값)
├── db.py                # 간단한 DB 연결 (MySQL)
├── 📁 controllers/      # 각 디바이스 컨트롤러 로직
│   ├── sort_controller.py     # 분류기 관련 로직
│   ├── env_controller.py      # 환경 제어 로직
│   └── access_controller.py   # 출입 관리 로직
├── 📁 api/              # REST API 엔드포인트
│   ├── sort_api.py            # 분류기 관련 API
│   ├── env_api.py             # 환경 관련 API
│   └── access_api.py          # 출입 관련 API
└── 📁 utils/            # 유틸리티 함수들
    ├── tcp_handler.py          # TCP 소켓 연결 관리
    └── websocket_manager.py    # WebSocket 연결 관리

📁 models : DB 모델 정의 (SQLAlchemy 기반)
ㄴ init.py : 패키지 초기화
ㄴ database.py : DB 연결 및 세션 구성
ㄴ item.py : 재고 물품 정보 모델
ㄴ employee.py : 직원 정보 모델
ㄴ access_log.py : 출입기록 저장 모델
ㄴ environment_log.py : 온습도 로그 저장 모델

📁 gui : GUI 파일
ㄴ 📁 components : 공통으로 사용되는 UI 요소
ㄴ 📁 resources : 이미지나, 아이콘 등의 정적 리소스
  ㄴ 📁 fonts : 폰트 폴더
  ㄴ 📁 icons : 아이콘 폴더
  ㄴ 📁 images : 이미지 폴더
  ㄴ 📁 styles : qss 폴더
ㄴ 📁 ui : pyqt designer로 만든 .ui 파일
ㄴ 📁 views : .ui파일을 작동하게 만드는 파일
ㄴ main_window.py : PyQt 진입점

📁 scripts : 자동화 스크립트 (GUI 실행, 서버 가동 등)
ㄴ run_all.sh


📁 test : 테스트 코드 및 시나리오
ㄴ 📁 simulator: 가상 시뮬레이션
   ㄴ bacode_simulator.py  : 바코드 시뮬레이터
```