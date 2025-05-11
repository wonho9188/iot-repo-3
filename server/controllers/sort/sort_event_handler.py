# server/controllers/sort_event_handler.py
import json
import logging
import threading
import time
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# ==== 분류기 이벤트 처리 클래스 ====
class SortEventHandler:
    # ==== 이벤트 핸들러 초기화 ====
    def __init__(self, controller, tcp_handler, shelf_manager):
        self.controller = controller
        self.tcp_handler = tcp_handler
        self.shelf_manager = shelf_manager
        
        # 바코드 처리중 상태
        self.processing_barcode = False
        
        # 자동 종료 타이머
        self.auto_stop_timer: Optional[threading.Timer] = None
        
        # 분류 정보
        self.category_map = {
            "1": "A",  # 냉동
            "2": "B",  # 냉장
            "3": "C",  # 상온
            "4": "D",  # 비식품
            "0": "E"   # 오류물품
        }
    
    # ==== 이벤트 메시지 처리 ====
    def handle_event(self, message: dict):
        try:
            if 'evt' not in message or 'val' not in message:
                logger.warning(f"잘못된 이벤트 메시지 형식: {json.dumps(message)}")
                return
            
            event_type = message['evt']
            values = message['val']
            
            # 이벤트 타입별 처리
            if event_type == "bc":
                # 바코드 인식 이벤트
                self._handle_barcode_event(values)
            elif event_type == "ir":
                # IR 센서 감지 이벤트
                self._handle_ir_sensor_event(values)
            elif event_type == "auto":
                # 자동 정지 이벤트
                self._handle_auto_stop_event(values)
            elif event_type == "emb":
                # 비상 정지 버튼 이벤트
                self._handle_emergency_button_event(values)
            elif event_type == "bcerr":
                # 바코드 인식 오류
                self._handle_barcode_error_event(values)
            else:
                logger.warning(f"알 수 없는 이벤트 타입: {event_type}")
        
        except Exception as e:
            logger.error(f"분류기 이벤트 처리 중 오류: {str(e)}")
    
    # ==== 응답 메시지 처리 ====
    def handle_response(self, message: dict):
        try:
            if 'res' not in message:
                logger.warning(f"잘못된 응답 메시지 형식: {json.dumps(message)}")
                return
            
            response_type = message['res']
            values = message.get('val', {})
            
            # 응답 타입별 처리
            if response_type == "ok":
                # 성공 응답 처리
                self._handle_ok_response(values)
            elif response_type == "err":
                # 오류 응답 처리
                self._handle_error_response(values)
            else:
                logger.warning(f"알 수 없는 응답 타입: {response_type}")
        
        except Exception as e:
            logger.error(f"분류기 응답 처리 중 오류: {str(e)}")
    
    # ==== 바코드 인식 이벤트 처리 ====
    def _handle_barcode_event(self, values: dict):
        if 'c' not in values:
            logger.warning("바코드 값이 없는 바코드 이벤트")
            return
        
        barcode = values['c']
        logger.info(f"바코드 인식: {barcode}")
        
        # 처리 중인 바코드가 없는지 확인 (중복 방지)
        if self.processing_barcode:
            logger.warning(f"이미 처리 중인 바코드가 있음: {barcode}")
            return
        
        self.processing_barcode = True
        
        try:
            # 바코드 파싱 (형식: 분류(1자리) + 물품번호(3자리) + 판매자(2자리) + 유통기한(6자리, YYMMDD))
            if len(barcode) < 12:
                logger.error(f"잘못된 바코드 형식: {barcode}")
                # 오류물품(E) 분류 명령 전송
                self._send_sort_command("E")
                return
                
            category_code = barcode[0]
            item_code = barcode[1:4]
            vendor_code = barcode[4:6]
            expiry_date = f"20{barcode[6:8]}-{barcode[8:10]}-{barcode[10:12]}"
            
            # 분류 카테고리 결정
            if category_code in self.category_map:
                warehouse = self.category_map[category_code]
            else:
                warehouse = "E"  # 알 수 없는 카테고리는 오류물품으로 분류
            
            # 선반 할당
            shelf = None
            if warehouse != "E":  # 오류물품(E)은 선반 할당 안함
                shelf = self.shelf_manager.assign_shelf(warehouse)
            
            # 분류 명령 전송
            self._send_sort_command(warehouse)
            
            # 항목 정보 생성
            item_info = {
                "barcode": barcode,
                "category": warehouse,
                "item_code": item_code,
                "vendor_code": vendor_code,
                "expiry_date": expiry_date,
                "shelf": shelf
            }
            
            # DB에 물품 정보 저장
            self.shelf_manager.save_item(item_info)
            
            # 웹소켓 이벤트 발송
            self.controller._emit_socketio_event("barcode_scanned", item_info)
            
            # 로그에 분류 정보 추가
            self.controller.sort_logs.append(item_info)
            if len(self.controller.sort_logs) > 10:
                self.controller.sort_logs.pop(0)  # 최근 10개만 유지
            
            # 자동 정지 타이머 초기화 (물품이 인식되었으므로)
            self.reset_auto_stop_timer()
        
        except Exception as e:
            logger.error(f"바코드 처리 중 오류: {str(e)}")
            # 오류 발생 시 오류물품(E)으로 분류
            self._send_sort_command("E")
        
        finally:
            self.processing_barcode = False
    
    # ==== IR 센서 감지 이벤트 처리 ====
    def _handle_ir_sensor_event(self, values: dict):
        if 'sn' not in values or 'v' not in values:
            logger.warning("센서 정보가 없는 IR 센서 이벤트")
            return
        
        sensor = values['sn']
        value = values['v']
        
        logger.debug(f"IR 센서 감지: {sensor}, 값: {value}")
        
        # 입구 센서 처리
        if sensor == "entry" and value == 1:
            self.controller.items_waiting += 1
            self.controller._update_status()
        
        # 분류대 센서 처리 (분류 영역 A, B, C, D, E)
        elif sensor in ["A", "B", "C", "D", "E"] and value == 1:
            # 대기 물품 감소
            if self.controller.items_waiting > 0:
                self.controller.items_waiting -= 1
            
            # 처리 물품 증가
            self.controller.items_processed += 1
            
            # 분류대별 카운터 증가
            self.controller.sorted_items[sensor] += 1
            
            # 상태 업데이트
            self.controller._update_status()
            
            # 해당 창고 물품 카운트 증가 (웹소켓 이벤트로)
            self.controller._emit_socketio_event("item_sorted", {
                "warehouse": sensor,
                "items_waiting": self.controller.items_waiting,
                "items_processed": self.controller.items_processed,
                "sorted_items": self.controller.sorted_items
            })
    
    # ==== 자동 정지 이벤트 처리 ====
    def _handle_auto_stop_event(self, values: dict):
        from .sort_controller import SortStatus  # 순환 참조 방지
        
        reason = values.get('r', 'unknown')
        logger.info(f"자동 정지 이벤트: {reason}")
        
        # 분류기 상태 변경
        self.controller.status = SortStatus.STOPPED.value
        self.controller.motor_active = False
        
        # 자동 정지 타이머 취소 (이미 정지됨)
        self.cancel_auto_stop_timer()
        
        # 웹소켓 이벤트 발송
        self.controller._emit_socketio_event("auto_stopped", {
            "reason": reason,
            "status": self.controller.status
        })
        
        # 상태 업데이트
        self.controller._update_status()
    
    # ==== 비상 정지 버튼 이벤트 처리 ====
    def _handle_emergency_button_event(self, values: dict):
        from .sort_controller import SortStatus  # 순환 참조 방지
        
        state = values.get('s', 0)
        logger.info(f"비상 정지 버튼 상태: {state}")
        
        # 물리적 비상 정지 상태 업데이트
        self.controller.physical_emergency = (state == 1)
        
        if self.controller.physical_emergency:
            # 비상 정지 상태로 변경
            self.controller.status = SortStatus.EMERGENCY_STOP.value
            self.controller.motor_active = False
            
            # 자동 정지 타이머 취소 (비상 정지됨)
            self.cancel_auto_stop_timer()
            
            # 웹소켓 이벤트 발송
            self.controller._emit_socketio_event("emergency_stop", {
                "physical_button": True,
                "status": self.controller.status
            })
        
        # 상태 업데이트
        self.controller._update_status()
    
    # ==== 바코드 인식 오류 이벤트 처리 ====
    def _handle_barcode_error_event(self, values: dict):
        error_code = values.get('c', 'unknown')
        logger.warning(f"바코드 인식 오류: {error_code}")
        
        # 오류물품(E) 분류 명령 전송
        self._send_sort_command("E")
        
        # 웹소켓 이벤트 발송
        self.controller._emit_socketio_event("barcode_error", {
            "error_code": error_code
        })
    
    # ==== 성공 응답 처리 ====
    def _handle_ok_response(self, values: dict):
        from .sort_controller import SortStatus  # 순환 참조 방지
        
        # 물리적 비상정지, 모터 상태, 상태 정보 처리
        if 'pe' in values:
            self.controller.physical_emergency = (values['pe'] == 1)
        
        if 'ma' in values:
            self.controller.motor_active = (values['ma'] == 1)
        
        if 'st' in values:
            received_status = values['st']
            
            # 상태 매핑
            if received_status == "run":
                new_status = SortStatus.RUNNING.value
            elif received_status == "stop":
                new_status = SortStatus.STOPPED.value
            elif received_status == "err":
                new_status = SortStatus.EMERGENCY_STOP.value
            else:
                new_status = self.controller.status  # 알 수 없는 상태는 변경하지 않음
            
            # 상태가 변경된 경우 업데이트
            if new_status != self.controller.status:
                self.controller.status = new_status
                self.controller._update_status()
    
    # ==== 오류 응답 처리 ====
    def _handle_error_response(self, values: dict):
        error_code = values.get('c', 'unknown')
        error_message = values.get('m', '알 수 없는 오류')
        
        logger.error(f"분류기 오류 응답: {error_code}, {error_message}")
        
        # 웹소켓 이벤트 발송
        self.controller._emit_socketio_event("sorter_error", {
            "error_code": error_code,
            "error_message": error_message
        })
    
    # ==== 분류 명령 전송 ====
    def _send_sort_command(self, zone: str):
        command = {
            "dev": "sr",
            "tp": "cmd",
            "cmd": "srv",
            "act": "sort",
            "val": {
                "z": zone
            }
        }
        
        success = self.tcp_handler.send_message("sr", command)
        if not success:
            logger.error(f"분류 명령 전송 실패: {zone}")
    
    # ==== 자동 정지 타이머 설정 ====
    def reset_auto_stop_timer(self):
        # 기존 타이머 취소
        self.cancel_auto_stop_timer()
        
        from .sort_controller import SortStatus  # 순환 참조 방지
        
        # 분류기가 작동 중인 경우에만 타이머 설정
        if self.controller.status == SortStatus.RUNNING.value:
            self.auto_stop_timer = threading.Timer(10.0, self._auto_stop_timeout)
            self.auto_stop_timer.daemon = True
            self.auto_stop_timer.start()
    
    # ==== 자동 정지 타이머 취소 ====
    def cancel_auto_stop_timer(self):
        if self.auto_stop_timer:
            self.auto_stop_timer.cancel()
            self.auto_stop_timer = None
    
    # ==== 자동 정지 타임아웃 처리 ====
    def _auto_stop_timeout(self):
        from .sort_controller import SortStatus  # 순환 참조 방지
        
        # 타이머 발생 시 분류기가 여전히 작동 중이고 대기 물품이 없는 경우
        if self.controller.status == SortStatus.RUNNING.value and self.controller.items_waiting == 0:
            logger.info("자동 정지: 10초간 물품 없음")
            
            # 정지 명령 전송
            command = {
                "dev": "sr",
                "tp": "cmd",
                "cmd": "inb",
                "act": "stop"
            }
            
            self.tcp_handler.send_message("sr", command)
            
            # 상태 업데이트
            self.controller.status = SortStatus.STOPPED.value
            self.controller.motor_active = False
            
            # 상태 업데이트 이벤트 발송
            self.controller._update_status()
            
            # Socket.IO 이벤트 발송
            self.controller._emit_socketio_event("auto_stopped", {
                "reason": "no_items_timeout",
                "status": self.controller.status
            })