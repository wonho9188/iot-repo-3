from datetime import datetime
from typing import Dict, Optional
from flask import Blueprint, jsonify, request

# Blueprint 초기화
router = Blueprint('sort', __name__, url_prefix='/api/sort')

# 컨트롤러 의존성
def get_sort_controller():
    """분류기 컨트롤러 인스턴스를 반환합니다."""
    try:
        from server.main import init_controllers
        controllers = init_controllers()
        return controllers["sort"]
    except ImportError:
        try:
            from main import init_controllers
            controllers = init_controllers()
            return controllers["sort"]
        except ImportError:
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from server.main import init_controllers
            controllers = init_controllers()
            return controllers["sort"]

@router.route("/start", methods=["POST"])
def start_sorting():
    """분류 작업을 시작합니다."""
    try:
        controller = get_sort_controller()
        result = controller.start_sorting()
        return jsonify({
            "status": "success",
            "message": "분류 작업이 시작되었습니다.",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@router.route("/stop", methods=["POST"])
def stop_sorting():
    """분류 작업을 중지합니다."""
    try:
        controller = get_sort_controller()
        result = controller.stop_sorting()
        return jsonify({
            "status": "success",
            "message": "분류 작업이 중지되었습니다.",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@router.route("/emergency/stop", methods=["POST"])
def emergency_stop():
    """비상 정지를 실행합니다."""
    try:
        controller = get_sort_controller()
        result = controller.emergency_stop()
        return jsonify({
            "status": "success",
            "message": "비상 정지가 실행되었습니다.",
            "timestamp": datetime.now().isoformat(),
            "auto_dismiss": False  # 수동으로 해제해야 함
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@router.route("/status", methods=["GET"])
def get_status():
    """현재 분류기 상태를 조회합니다."""
    try:
        controller = get_sort_controller()
        status = controller.check_status()
        return jsonify({
            "status": "success",
            "current_status": status["status"],
            "waiting_count": status["waiting"],
            "processed_count": status["processed"],
            "timestamp": status["timestamp"]
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500
