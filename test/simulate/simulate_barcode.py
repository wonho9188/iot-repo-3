import time
import json
import paho.mqtt.client as mqtt
import ssl

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✔️ 연결 성공")
        # 메시지 전송
        data = {
            "pid": "0101",
            "comp": "99",
            "exp": "250803",
            "ts": int(time.time())
        }
        client.publish("v1/conv/bc/01/scan", json.dumps(data), qos=1)
    else:
        print(f"❌ 연결 실패: {rc}")

client = mqtt.Client()
client.tls_set(ca_certs="/etc/mosquitto/certs/ca.crt", tls_version=ssl.PROTOCOL_TLSv1_2)
client.tls_insecure_set(True)
client.on_connect = on_connect

client.connect("192.168.0.3", 1883, 60)
client.loop_start()
time.sleep(2)
client.loop_stop()
client.disconnect()