# server/api/__init__.py
from flask import Blueprint, jsonify, request
from typing import Dict, Any, Optional

# 블루프린트 정의 (bp로 이름 변경)
bp = Blueprint('api', __name__)

# 컨트롤러 참조 설정
controller: Optional[Any] = None

# 컨트롤러 설정 함수
def set_controller(main_controller):
    global controller
    controller = main_controller