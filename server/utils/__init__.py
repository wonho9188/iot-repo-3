# server/api/__init__.py
from flask import Blueprint, jsonify, request
from typing import Dict, Any, Optional

# 블루프린트 정의
api_bp = Blueprint('api', __name__, url_prefix='/api')

# 각 모듈별 엔드포인트 정의
from .sort_api import *
from .env_api import *
from .access_api import *
from .expiry_api import *

# 컨트롤러 참조 설정
controller: Optional[Any] = None

# 컨트롤러 설정 함수
def set_controller(main_controller):
    global controller
    controller = main_controller