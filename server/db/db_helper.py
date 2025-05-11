# server/db/db_helper.py
import logging
import mysql.connector
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

logger = logging.getLogger(__name__)

class DBHelper:
    def __init__(self):
        """DB 헬퍼 초기화"""
        # DB 연결 정보
        self.host = os.getenv("DB_HOST", "localhost")
        self.user = os.getenv("DB_USER", "railuser")
        self.password = os.getenv("DB_PASSWORD", "railpass")
        self.database = os.getenv("DB_NAME", "rail_db")
        
        self.conn = None
        self.connect()
        logger.info("DB 헬퍼 초기화 완료")
    
    def connect(self) -> bool:
        """MySQL 데이터베이스 연결"""
        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            logger.info("MySQL 데이터베이스 연결 성공")
            return True
        except Exception as e:
            logger.error(f"MySQL 데이터베이스 연결 실패: {str(e)}")
            self.conn = None
            return False
    
    def ensure_connection(self) -> bool:
        """연결 확인 및 필요 시 재연결"""
        if not self.conn or not self.conn.is_connected():
            return self.connect()
        return True
    
    def execute_query(self, query: str, params: Tuple = None, fetch: bool = False) -> Optional[List[Tuple]]:
        """쿼리 실행 유틸리티 메소드"""
        if not self.ensure_connection():
            logger.error("DB 연결 없음 - 쿼리 실행 불가")
            return None
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            
            result = None
            if fetch:
                result = cursor.fetchall()
            else:
                self.conn.commit()
            
            cursor.close()
            return result
        except Exception as e:
            logger.error(f"쿼리 실행 실패: {str(e)}")
            logger.error(f"쿼리: {query}, 파라미터: {params}")
            return None
    
    # ===== 선반 관련 기능 =====
    
    def get_empty_shelves(self, warehouse: str) -> List[str]:
        """지정된 창고의 빈 선반 목록 조회"""
        query = """
            SELECT shelf_id FROM shelves 
            WHERE warehouse = %s AND status = 'empty'
            ORDER BY shelf_id ASC
        """
        
        result = self.execute_query(query, (warehouse,), True)
        if result is None:
            return []
        
        return [row[0] for row in result]
    
    def update_shelf_status(self, warehouse: str, shelf_id: str, status: str) -> bool:
        """선반 상태 업데이트"""
        query = """
            UPDATE shelves 
            SET status = %s, updated_at = %s
            WHERE warehouse = %s AND shelf_id = %s
        """
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        result = self.execute_query(query, (status, current_time, warehouse, shelf_id))
        
        return result is not None
    
    # ===== 물품 관련 기능 =====
    
    def save_item(self, item_info: dict) -> bool:
        """물품 정보 저장"""
        query = """
            INSERT INTO items 
            (barcode, category, item_code, vendor_code, expiry_date, 
            warehouse, shelf, entry_date, status, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # 현재 날짜/시간
        now = datetime.now()
        entry_date = now.strftime('%Y-%m-%d')
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
        
        values = (
            item_info.get('barcode'),
            item_info.get('category'),
            item_info.get('item_code'),
            item_info.get('vendor_code'),
            item_info.get('expiry_date'),
            item_info.get('category'),  # 카테고리가 창고명과 동일
            item_info.get('shelf'),
            entry_date,
            'active',
            timestamp,
            timestamp
        )
        
        result = self.execute_query(query, values)
        return result is not None
    
    def get_warehouse_items_count(self, warehouse: str) -> int:
        """특정 창고의 물품 수량 조회"""
        query = """
            SELECT COUNT(*) FROM items 
            WHERE warehouse = %s AND status = 'active'
        """
        
        result = self.execute_query(query, (warehouse,), True)
        if result is None or not result:
            return 0
        
        return result[0][0]
    
    def get_expiring_items(self, days: int = 3) -> Dict[str, List[Dict[str, Any]]]:
        """유통기한이 임박하거나 지난 물품 조회"""
        # 1. 이미 지난 유통기한 물품
        expired_query = """
            SELECT id, barcode, item_code, warehouse, shelf, expiry_date 
            FROM items 
            WHERE status = 'active' AND expiry_date < CURDATE()
            ORDER BY expiry_date ASC
        """
        
        # 2. 오늘 만료되는 물품
        today_query = """
            SELECT id, barcode, item_code, warehouse, shelf, expiry_date 
            FROM items 
            WHERE status = 'active' AND expiry_date = CURDATE()
            ORDER BY expiry_date ASC
        """
        
        # 3. N일 이내 만료 예정 물품
        upcoming_query = """
            SELECT id, barcode, item_code, warehouse, shelf, expiry_date 
            FROM items 
            WHERE status = 'active' 
              AND expiry_date > CURDATE() 
              AND expiry_date <= DATE_ADD(CURDATE(), INTERVAL %s DAY)
            ORDER BY expiry_date ASC
        """
        
        # 각 쿼리 실행
        expired_result = self.execute_query(expired_query, None, True) or []
        today_result = self.execute_query(today_query, None, True) or []
        upcoming_result = self.execute_query(upcoming_query, (days,), True) or []
        
        # 결과 포맷팅
        def format_items(items):
            return [{
                'id': item[0],
                'barcode': item[1],
                'item_code': item[2], 
                'warehouse': item[3],
                'shelf': item[4],
                'expiry_date': item[5].strftime('%Y-%m-%d')
            } for item in items]
        
        return {
            'expired': format_items(expired_result),
            'today': format_items(today_result),
            'upcoming': format_items(upcoming_result)
        }
    
    # ===== 환경 관련 기능 =====
    
    def save_environment_data(self, warehouse: str, temp: float, humidity: float = None, status: str = 'normal') -> bool:
        """환경 데이터 저장 (온도, 습도)"""
        query = """
            INSERT INTO environment_logs 
            (warehouse, temperature, humidity, status, created_at)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        result = self.execute_query(query, (warehouse, temp, humidity, status, timestamp))
        
        return result is not None
    
    def get_latest_environment_data(self, warehouse: str = None) -> List[Dict[str, Any]]:
        """최신 환경 데이터 조회"""
        if warehouse:
            query = """
                SELECT warehouse, temperature, humidity, status, created_at
                FROM environment_logs
                WHERE warehouse = %s
                ORDER BY created_at DESC
                LIMIT 1
            """
            result = self.execute_query(query, (warehouse,), True)
        else:
            # 모든 창고의 최신 데이터 조회
            query = """
                SELECT e.warehouse, e.temperature, e.humidity, e.status, e.created_at
                FROM environment_logs e
                INNER JOIN (
                    SELECT warehouse, MAX(created_at) as max_date
                    FROM environment_logs
                    GROUP BY warehouse
                ) as latest
                ON e.warehouse = latest.warehouse AND e.created_at = latest.max_date
            """
            result = self.execute_query(query, None, True)
        
        if result is None:
            return []
        
        return [{
            'warehouse': row[0],
            'temperature': row[1],
            'humidity': row[2],
            'status': row[3],
            'timestamp': row[4].strftime('%Y-%m-%d %H:%M:%S')
        } for row in result]
    
    # ===== 출입 관련 기능 =====
    
    def check_rfid_access(self, rfid_uid: str) -> Dict[str, Any]:
        """RFID 카드 출입 권한 확인"""
        query = """
            SELECT e.id, e.name, e.department, e.access_level
            FROM employees e
            JOIN employee_cards ec ON e.id = ec.employee_id
            WHERE ec.card_uid = %s AND e.status = 'active'
        """
        
        result = self.execute_query(query, (rfid_uid,), True)
        if not result:
            return {'status': 'denied', 'reason': 'card_not_found'}
        
        employee = {
            'id': result[0][0],
            'name': result[0][1],
            'department': result[0][2],
            'access_level': result[0][3],
            'status': 'approved'
        }
        
        return employee
    
    def log_access_event(self, employee_id: str, event_type: str, gate_id: str = 'main') -> bool:
        """출입 이벤트 로깅"""
        query = """
            INSERT INTO access_logs
            (employee_id, event_type, gate_id, timestamp)
            VALUES (%s, %s, %s, %s)
        """
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        result = self.execute_query(query, (employee_id, event_type, gate_id, timestamp))
        
        return result is not None
    
    def get_access_logs(self, date: str = None, employee_id: str = None) -> List[Dict[str, Any]]:
        """출입 기록 조회"""
        params = []
        conditions = []
        
        query = """
            SELECT al.id, al.employee_id, e.name, e.department, 
                   al.event_type, al.gate_id, al.timestamp
            FROM access_logs al
            JOIN employees e ON al.employee_id = e.id
            WHERE 1=1
        """
        
        if date:
            conditions.append("DATE(al.timestamp) = %s")
            params.append(date)
        
        if employee_id:
            conditions.append("al.employee_id = %s")
            params.append(employee_id)
        
        if conditions:
            query += " AND " + " AND ".join(conditions)
        
        query += " ORDER BY al.timestamp DESC"
        
        result = self.execute_query(query, tuple(params), True)
        if result is None:
            return []
        
        return [{
            'id': row[0],
            'employee_id': row[1],
            'name': row[2],
            'department': row[3],
            'event_type': row[4],
            'gate_id': row[5],
            'timestamp': row[6].strftime('%Y-%m-%d %H:%M:%S')
        } for row in result]