import json
import time
import logging
import paho.mqtt.client as mqtt
import requests
from typing import Dict, Any, Callable
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent     # 상대 경로를 사용하여 루트 디렉토리 찾기
sys.path.insert(0, str(ROOT_DIR))

from config import CONFIG

# ===== 로거 설정 =====
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger("mqtt_client")

# ===== 하드웨어 장치들과의 통신 담당 =====
class MQTTClient:
    
    _instance = None  # 싱글톤 인스턴스
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MQTTClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self.client_id = CONFIG["MQTT_CLIENT_ID"]
        self.broker = CONFIG["MQTT_BROKER"]
        self.port = CONFIG["MQTT_PORT"]
        self.topic_prefix = CONFIG["TOPIC_PREFIX"]
        
        # 토픽별 콜백 함수 저장
        self.topic_handlers = {}         # 토픽별 콜백 함수 저장
        self.topic_handlers = {}
        VVVV
        
        # MQTT 클라이언트 생성
        self.client = mqtt.Client(client_id=self.client_id, protocol=mqtt.MQTTv311)
        
        # 콜백 함수 설정
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        
        # 연결 상태
        self.connected = False
        
    def connect(self):
        try:
            logger.info(f"MQTT 브로커 {self.broker}:{self.port}에 연결 시도...")
            self.client.connect(self.broker, self.port, 60)
            
            # 네트워크 루프 시작 (별도 스레드에서 실행)
            self.client.loop_start()
            
            # 연결 대기 (최대 5초)
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < 5:
                time.sleep(0.1)
                
            return self.connected
        except Exception as e:
            logger.error(f"MQTT 브로커 연결 실패: {str(e)}")
            return False
            
    def disconnect(self):
        """MQTT 브로커 연결 종료"""
        if self.connected:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("MQTT 브로커 연결 종료")
            
    def subscribe(self, topic, callback):
        """특정 토픽 구독 및 콜백 함수 등록"""
        full_topic = f"{self.topic_prefix}{topic}"
        
        # 토픽별 콜백 등록
        self.topic_handlers[full_topic] = callback
        
        # 이미 연결된 경우 즉시 구독
        if self.connected:
            self.client.subscribe(full_topic)
            logger.info(f"토픽 구독: {full_topic}")
            
    def publish(self, topic, payload, qos=0):
        """특정 토픽에 메시지 발행"""
        if not self.connected:
            logger.error("MQTT 브로커에 연결되어 있지 않음")
            return
            
        full_topic = f"{self.topic_prefix}{topic}"
        
        # 타임스탬프 추가
        if 'ts' not in payload:
            payload['ts'] = int(time.time())
            
        # JSON으로 변환하여 발행
        message = json.dumps(payload)
        self.client.publish(full_topic, message, qos)
        logger.debug(f"메시지 발행: {full_topic} - {message}")
        
    def post_to_server(self, endpoint, data):
        """서버 API로 데이터 전송"""
        server_url = f"http://{CONFIG['HOST']}:{CONFIG['PORT']}{endpoint}"
        try:
            response = requests.post(server_url, json=data, timeout=2)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"서버 요청 실패: {str(e)}")
            return False
        
    def _on_connect(self, client, userdata, flags, rc):
        """MQTT 브로커 연결 콜백"""
        if rc == 0:
            logger.info("MQTT 브로커에 연결됨")
            self.connected = True
            
            # 등록된 모든 토픽 구독
            for topic in self.topic_handlers:
                self.client.subscribe(topic)
                logger.info(f"토픽 구독: {topic}")
        else:
            logger.error(f"MQTT 브로커 연결 실패: {rc}")
            
    def _on_message(self, client, userdata, msg):
        """메시지 수신 콜백"""
        topic = msg.topic
        try:
            # JSON 메시지 파싱
            payload = json.loads(msg.payload.decode('utf-8'))
            
            # 토픽 콜백 함수 호출
            if topic in self.topic_handlers:
                self.topic_handlers[topic](payload)
                
        except json.JSONDecodeError:
            logger.error(f"잘못된 JSON 형식: {msg.payload}")
        except Exception as e:
            logger.error(f"메시지 처리 중 오류: {str(e)}")

# 싱글톤 인스턴스 접근 함수
def get_mqtt_client():
    """MQTT 클라이언트 인스턴스 반환"""
    return MQTTClient()

# 테스트 코드
if __name__ == "__main__":
    # 바코드 콜백 함수
    def handle_barcode(payload):
        logger.info(f"바코드 수신: {payload}")
        
        # 유효성 검사
        if "pid" not in payload or "exp" not in payload:
            logger.warning("필수 필드 누락 (pid/exp)")
            return
            
        # 서버로 전송
        mqtt_client.post_to_server("/inventory/in", payload)
    
    # MQTT 클라이언트 시작
    mqtt_client = get_mqtt_client()
    mqtt_client.subscribe("conv/bc/+/scan", handle_barcode)
    
    if mqtt_client.connect():
        logger.info("MQTT 클라이언트 실행 중...")
        
        try:
            # 프로그램 계속 실행
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("프로그램 종료")
            mqtt_client.disconnect()