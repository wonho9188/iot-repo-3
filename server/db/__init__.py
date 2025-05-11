import mysql.connector
from mysql.connector import Error

password = '0000'  # MySQL 비밀번호를 입력하세요

def create_database():
    try:
        # MySQL에 연결
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password = password  # root 비밀번호를 입력하세요
        )

        if connection.is_connected():
            cursor = connection.cursor()
            # 데이터베이스 생성
            cursor.execute("CREATE DATABASE IF NOT EXISTS rail_db;")
            print("Database 'rail_db' created successfully!")
    
    except Error as e:
        print(f"Error: {e}")
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")

if __name__ == "__main__":
    create_database()