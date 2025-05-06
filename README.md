# iot-repo-3

## 폴더 별 역할
📁 controller : 시스템 간 데이터 흐름 조정
ㄴ 📁 api : 서버와의 통신
ㄴ 📁 arduino : 하드웨어(아두이노)와 통신
ㄴ 📁 logic : 기능 별 로직

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
ㄴ 📁 models : DB 모델 정의 (사용자, 로그 등)
ㄴ 📁 services : 비즈니스 로직 ()
ㄴ app.py : 서버 진입점
ㄴ config.py : 설정 (DB, 포트 등)

📁 test : 테스트 코드 및 시나리오