import time
import json
import random
import paho.mqtt.client as mqtt
from datetime import datetime, timedelta

# MQTT 브로커 정보
MQTT_HOST = "localhost"  # 브로커 IP
MQTT_PORT = 1883            # 기본 포트 (비암호화)

# 랜덤 바코드 데이터 생성 함수
def generate_barcode_data():
    pid = f"{random.randint(1, 99):02d}{random.randint(1, 99):02d}"
    comp = f"{random.randint(10, 99)}"
    future_date = datetime.now() + timedelta(days=random.randint(1, 180))
    exp = future_date.strftime("%y%m%d")
    ts = int(time.time())
    return {
        "pid": pid,
        "comp": comp,
        "exp": exp,
        "ts": ts
    }

# MQTT 연결 콜백
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✔️ 연결 성공")
    else:
        print(f"❌ 연결 실패: {rc}")

# MQTT 클라이언트 설정
client = mqtt.Client(protocol=mqtt.MQTTv311)
client.on_connect = on_connect

client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
client.loop_start()

try:
    while True:
        data = generate_barcode_data()
        print("발행 →", data)
        client.publish("v1/conv/bc/01/scan", json.dumps(data), qos=1)
        time.sleep(5)  # 🔁 5초 간격
except KeyboardInterrupt:
    print("\n🛑 중단됨: 시뮬레이션 종료")
finally:
    client.loop_stop()
    client.disconnect()