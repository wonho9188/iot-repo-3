# iot-repo-3

## 폴더 별 역할
```
📁 controller/     : 시스템 간 데이터 흐름을 조정
ㄴ 📁 api/         : 서버(FastAPI)와 통신하는 HTTP/WebSocket 클라이언트 로직
  ㄴ __init__.py    : 모듈 초기화
  ㄴ client.py      : REST API 호출, WebSocket 연결 관리
ㄴ 📁 arduino/      : Arduino(ESP32 포함)와 직렬(Serial) 통신 관리
  ㄴ __init__.py    : 모듈 초기화
  ㄴ serial_manager.py : USB/UART 포트 열기·읽기·쓰기 로직
  ㄴ protocol.py       : 아두이노 간 커맨드·응답 패킷 포맷 정의
ㄴ 📁 logic/           : 핵심 비즈니스 흐름(기능) 구현
  ㄴ inventory_logic.py  : 입고·출고·재고 관리 로직
  ㄴ environment.py    : 온습도 모니터링 및 제어 로직
  ㄴ notification.py   : 알림·경고 트리거 처리

📁 docs : 설명 문서
ㄴ CODE_STANDARD.md : 코딩 스탠다드

📁 firmware : C++ 기반 아두이노 관리 폴더 (ino 확장자)
ㄴ 📁 modules : 모듈 폴더
ㄴ main.ino : 진입점, setup()과 loop()만 존재
ㄴ config.h : 핀 번호, 상수 정의

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

📁 server : 백엔드 로직
ㄴ 📁 database : DB 연결 및 쿼리
  ㄴ __init__.py : SQLAlchemy 세션/엔진 초기화
ㄴ 📁 models : DB 모델 정의 (사용자, 로그 등)
  ㄴ  inventory_model.py : 재고 관련 테이블 
ㄴ 📁 services : 비즈니스 로직 ()
  ㄴ inventory_service.py : 재고 CRUD 및 검증 처리
ㄴ 📁 routers : API 엔드포인트 그룹화 (FastAPI 라우터)
  ㄴ inventory_router.py   : items 관련 REST API 정의  
ㄴ app.py : FastAPI 애플리케이션 인스턴스 생성 및 라우터 등록
ㄴ config.py : 설정 (DB, 포트 등)

📁 test : 테스트 코드 및 시나리오
```