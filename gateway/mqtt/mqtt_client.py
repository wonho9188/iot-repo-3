import paho.mqtt.client as mqtt  # MQTT 클라이언트
import ssl         # TLS/SSL 통신을 위한 보안 모듈
import json        # JSON 데이터 처리
import time        # 시간 관련 기능 
import requests   # server로 HTTP 요청을 보낼 수 있는 모듈


# =====  MQTT 연결 시 호출되는 콜백함수 ===== 
def on_connect(client, userdata, flags, rc):
    if rc == 0 :
        print("gateway MQTT 연결 완료")
    else:
        print(f"연결실패 : {rc}")
    client.subscribe("v1/conv/bc/+/scan", qos=1)
 
# =====  메시지 수신 시 호출되는 콜백 ===== 
def on_message(client, userdata, msg):
    try:
        payload_str = msg.payload.decode() 
        data = json.loads(payload_str)      # 수신된 메시지(json 문자열)을 python 객체로 변환 
        print(f"바코드수신: {data}")
    
        # 유효성 검사
        if "pid" not in data or "exp" not in data:
            print("필드 누락 !! (pid/exp)")
            return
        
        print("유효한 바코드 수신 :", data)

        #서버로 전송
        try:
            response =requests.post("http://192.168.0.3:8000/inventory/in", json = data)
            print("서버응답 :", response.status_code, response.text)  # request 모듈의 응답 객체를 제공하는 속성들
        except requests.exceptions.ReauestException as e :
            print("서버 전송 실패 :",e)

    except json.JSONDecodeError:
        print("json 파싱 실패: ", msg.payload)
    
    except Exception as e:
        print("예외 발생~~!", e)

         