# server/utils/tcp_handler.py
import socket
import threading
import json
import logging
import time
from typing import Dict, Callable, List, Any, Optional # 타입 힌트 정의시 사용하는 타입 도구
# 로거 설정
logger = logging.getLogger(__name__)


# ====  TCP 소켓 통신을 관리하는 핸들러 클래스 ====
class TCPHandler:
    # ==== TCPHandler 초기화 ====
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients: Dict[str, socket.socket] = {} # 클라이언트 소켓 저장 (디바이스 ID: 소켓)
        self.client_addresses: Dict[str, str] = {}  # 디바이스 주소 저장 (디바이스 ID: 주소)
        self.running = False         # 서버 실행 상태
        
        # 이벤트 핸들러 등록 (이벤트 타입: 핸들러 함수 리스트) 
        self.event_handlers: Dict[str, List[Callable]] = {
            "connect": [],      # 연결 이벤트
            "disconnect": [],   # 연결 해제 이벤트
            "message": [],      # 메시지 수신 이벤트
            "error": []         # 오류 이벤트
        }
        # 디바이스별 메시지 타입 핸들러 (디바이스 ID: {메시지 타입: 핸들러 함수})
        self.device_handlers: Dict[str, Dict[str, Callable]] = {}
    
    
    # ==== TCP 서버를 시작, 연결 대기 (return: 서버시작 성공여부) ====
    def start(self):
        if self.running:
            logger.warning("TCP 서버가 이미 실행 중입니다.") # 경고형식 로그 남김
            return True
        try:
            # 소켓 생성
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # 서버 재시작 시 "Address already in use" 오류 방지
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port)) # 주소와 포트에 바인딩
            self.server_socket.listen(5)                    # 연결 대기 시작(5개)    
            self.running = True         # 서버 상태 업데이트
            logger.info(f"TCP 서버가 {self.host}:{self.port}에서 시작되었습니다.")
            
            # 클라이언트 연결 수신 스레드 시작 (데몬 스레드로 설정)
            threading.Thread(target=self._accept_connections, daemon=True).start()
            return True 
        except Exception as e:
            logger.error(f"TCP 서버 시작 실패: {str(e)}")
            return False
        

    # ==== TCP 서버를 중지 후 클라이언트 연결을 종료 ====
    def stop(self):
        self.running = False

        # 모든 클라이언트 연결 종료
        for device_id, client_socket in list(self.clients.items()):
            self._close_client(device_id, client_socket)
        # 서버 소켓 종료
        if self.server_socket:
            try:
                self.server_socket.close()
                logger.info("TCP 서버가 중지되었습니다.")
            except Exception as e:
                logger.error(f"TCP 서버 종료 오류: {str(e)}")
    

    # ==== 클라이언트 연결을 수신하는 스레드 함수 ====
    def _accept_connections(self):
        while self.running:
            try:
                # 클라이언트 연결 수락 (차단 호출)
                client_socket, address = self.server_socket.accept()
                client_address = f"{address[0]}:{address[1]}"
                logger.info(f"새 클라이언트 연결: {client_address}")
                
                # 각 클라이언트에 대한 수신 스레드 시작
                threading.Thread(
                    target=self._handle_client, 
                    args=(client_socket, client_address),
                    daemon=True
                ).start()
            
            except Exception as e:
                if self.running:  # 의도적 종료가 아닌 경우에만 오류 기록
                    logger.error(f"클라이언트 연결 수신 오류: {str(e)}")
                break
    
    # ====  클라이언트 소켓에서 데이터 수신 후 처리 ====
    def _handle_client(self, client_socket: socket.socket, address: str):
        """
        Args:
            client_socket: 클라이언트 소켓
            address: 클라이언트 주소 문자열
        """
        device_id = None  # 아직 디바이스 ID를 모름
        buffer = b""      # 데이터 버퍼
        
        while self.running:
            try:
                # 데이터 수신 (최대 1024 바이트)
                data = client_socket.recv(1024)
                
                # 연결 종료 체크
                if not data:
                    logger.info(f"클라이언트 연결 종료: {address}")
                    break
                
                # 버퍼에 데이터 추가
                buffer += data
                
                # 완전한 메시지 처리 (여러 메시지가 한 번에 올 수 있음)
                # 각 메시지는 개행 문자로 구분
                while b'\n' in buffer:
                    # 첫 번째 개행 문자로 메시지 분리
                    message, buffer = buffer.split(b'\n', 1)
                    
                    try:
                        # UTF-8로 디코딩
                        decoded_message = message.decode('utf-8')
                        
                        # JSON 파싱
                        message_data = json.loads(decoded_message)
                        
                        # 디바이스 ID 확인 및 등록
                        if 'dev' in message_data:
                            current_device_id = message_data['dev']
                            
                            if device_id is None:
                                # 새 디바이스 등록
                                device_id = current_device_id
                                self.clients[device_id] = client_socket
                                self.client_addresses[device_id] = address
                                logger.info(f"디바이스 등록: {device_id} ({address})")
                                
                                # 연결 이벤트 발생
                                self._trigger_event("connect", device_id, client_socket)
                            
                            # 메시지 처리
                            self._process_message(device_id, message_data)
                        else:
                            logger.warning(f"디바이스 ID가 없는 메시지: {decoded_message}")
                    
                    except json.JSONDecodeError:
                        logger.error(f"잘못된 JSON 형식: {message}")
                    except Exception as e:
                        logger.error(f"메시지 처리 오류: {str(e)}")
            
            except ConnectionResetError:
                logger.info(f"클라이언트 연결 재설정: {address}")
                break
            except Exception as e:
                logger.error(f"클라이언트 처리 오류: {str(e)}")
                break
        
        # 연결 종료 처리
        if device_id:
            self._close_client(device_id, client_socket)
    
    def _process_message(self, device_id: str, message: dict):
        """
        수신된 메시지를 처리합니다.
        Args:
            device_id: 디바이스 ID
            message: 파싱된 메시지 데이터
        """
        try:
            # 기본 로깅 (디버그 레벨)
            logger.debug(f"메시지 수신 ({device_id}): {json.dumps(message)}")
            
            # 메시지 타입에 따른 처리
            if 'tp' in message:
                message_type = message['tp']
                
                # 디바이스별 핸들러 호출
                if device_id in self.device_handlers and message_type in self.device_handlers[device_id]:
                    # 등록된 핸들러 호출
                    self.device_handlers[device_id][message_type](message)
                
                # 글로벌 메시지 이벤트 트리거
                self._trigger_event("message", device_id, message)
            else:
                logger.warning(f"메시지 타입이 없는 메시지: {json.dumps(message)}")
        
        except Exception as e:
            logger.error(f"메시지 처리 중 오류: {str(e)}")
            self._trigger_event("error", device_id, {"error": str(e), "message": message})
    
    def _close_client(self, device_id: str, client_socket: socket.socket):
        """
        클라이언트 연결을 종료합니다.
        Args:
            device_id: 디바이스 ID
            client_socket: 클라이언트 소켓
        """
        try:
            # 소켓 닫기
            client_socket.close()
            
            # 클라이언트 목록에서 제거
            if device_id in self.clients:
                del self.clients[device_id]
            
            # 주소 목록에서 제거
            if device_id in self.client_addresses:
                del self.client_addresses[device_id]
            
            # 연결 종료 이벤트 발생
            self._trigger_event("disconnect", device_id, None)
            
            logger.info(f"클라이언트 연결 종료됨: {device_id}")
        
        except Exception as e:
            logger.error(f"클라이언트 종료 오류: {str(e)}")
    
    def send_message(self, device_id: str, message: dict) -> bool:
        """
        지정된 디바이스에 메시지를 전송합니다.
        Args:
            device_id: 대상 디바이스 ID
            message: 전송할 메시지 데이터
        Returns:
            bool: 전송 성공 여부
        """
        # 디바이스 ID 확인
        if device_id not in self.clients:
            logger.error(f"알 수 없는 디바이스 ID: {device_id}")
            return False
        
        try:
            # 클라이언트 소켓 가져오기
            client_socket = self.clients[device_id]
            
            # 메시지를 JSON 문자열로 변환 (개행 문자 추가)
            message_str = json.dumps(message) + '\n'
            
            # 전송
            client_socket.sendall(message_str.encode('utf-8'))
            
            # 로그 (디버그 레벨)
            logger.debug(f"메시지 전송 ({device_id}): {json.dumps(message)}")
            return True
        
        except Exception as e:
            logger.error(f"메시지 전송 오류 ({device_id}): {str(e)}")
            
            # 연결 오류 시 클라이언트 종료
            self._close_client(device_id, self.clients[device_id])
            return False
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """
        이벤트 핸들러를 등록합니다.
        Args:
            event_type: 이벤트 타입 ("connect", "disconnect", "message", "error")
            handler: 이벤트 핸들러 함수
        """
        if event_type in self.event_handlers:
            self.event_handlers[event_type].append(handler)
        else:
            logger.warning(f"알 수 없는 이벤트 타입: {event_type}")
    
    def register_device_handler(self, device_id: str, message_type: str, handler: Callable):
        """
        디바이스별 메시지 타입 핸들러를 등록합니다.
        
        Args:
            device_id: 디바이스 ID (예: "sr" - 분류기)
            message_type: 메시지 타입 (예: "evt" - 이벤트)
            handler: 핸들러 함수
        """
        # 디바이스 ID에 대한 핸들러 딕셔너리가 없으면 생성
        if device_id not in self.device_handlers:
            self.device_handlers[device_id] = {}
        
        # 핸들러 등록
        self.device_handlers[device_id][message_type] = handler
        logger.debug(f"디바이스 핸들러 등록: {device_id}, {message_type}")
    
    def _trigger_event(self, event_type: str, device_id: str, data: Any):
        """
        등록된 이벤트 핸들러들을 트리거합니다.
        
        Args:
            event_type: 이벤트 타입
            device_id: 디바이스 ID
            data: 이벤트 데이터
        """
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(device_id, data)
                except Exception as e:
                    logger.error(f"이벤트 핸들러 오류: {str(e)}")