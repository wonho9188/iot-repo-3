# iot-repo-3

## 폴더 별 역할
```

📁 docs : 설명 문서
ㄴ CODE_STANDARD.md : 코딩 스탠다드
ㄴ .env   : 시스템의 모든 설정을 중앙화
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

📁 gateway              :  하드웨어-GUI 사이의 중앙 통신 및 비즈니스 로직 
ㄴ app.py                :  서버 진입점
ㄴ config.py             :  설정 파일
ㄴdatabase.py            :  데이터베이스 연결 및 모델
ㄴ mqtt_handler.py       :  MQTT 메시지 처리
ㄴ api_routes.py         :  API 라우트 정의
ㄴ websocket_handler.py  :  WebSocket 처리
ㄴ requirements.txt      :  의존성 패키지 목록

📁 server   : 백엔드 서버 (FastAPI 기반)
ㄴ 📁 routers                  : REST API 엔드포인트 정의
   ㄴ inventory_router.py      : 입출고 관련 라우팅
   ㄴ access_router.py         : 출입관리 라우팅
ㄴ 📁 services                 : 주요 도메인 로직 구현 (입출고, 출입 기록, 경고 판단)
   ㄴ inventory_service.py     : 입고/출고 처리 및 구역 배정
   ㄴ access_service.py        : 출입 기록 판단 및 저장
   ㄴ expiry_service.py        : 유통기한 임박 판단
ㄴ 📁 models                   : SQLAlchemy 기반 DB 모델 정의
   ㄴ inventory_model.py       : 재고 DB 모델
   ㄴ access_model.py          : 출입 DB 모델
ㄴ 📁 schemas                  : Pydantic 요청/응답 스키마 (유효성 검사를 해주는 도구)
   ㄴ inventory_schema.py      : 재고 관련 요청/응답 구조 정의
   ㄴ access_schema.py         : 출입 관련 요청/응답 구조 정의
ㄴ 📁 database                 : DB 연결 초기화 및 세션 관리
   ㄴ __init__.py
ㄴ config.py                  : 환경설정 (DB URL, 포트, 시크릿 등)
ㄴ app.py                     : FastAPI 진입점 (라우터 등록, 실행)

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