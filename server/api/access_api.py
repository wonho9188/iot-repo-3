from datetime import datetime
from typing import Dict, List, Optional
from flask import Blueprint, jsonify, request

# Blueprint 초기화
bp = Blueprint('access', __name__)

# 컨트롤러 의존성
def get_access_controller():
    """출입 제어 컨트롤러 인스턴스를 반환합니다."""
    try:
        from server.main import init_controllers
        controllers = init_controllers()
        return controllers["access"]
    except ImportError:
        try:
            from main import init_controllers
            controllers = init_controllers()
            return controllers["access"]
        except ImportError:
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from server.main import init_controllers
            controllers = init_controllers()
            return controllers["access"]

@bp.route("/logs", methods=["GET"])
def get_access_logs():
    """출입 기록 조회"""
    try:
        controller = get_access_controller()
        logs = controller.get_access_logs()
        return jsonify({
            "success": True, 
            "logs": logs,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@bp.route("/open-door", methods=["POST"])
def open_door():
    """출입문 열기"""
    try:
        controller = get_access_controller()
        result = controller.open_door()
        return jsonify({
            "success": True, 
            "message": "출입문이 열렸습니다.",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@bp.route("/close-door", methods=["POST"])
def close_door():
    """출입문 닫기"""
    try:
        controller = get_access_controller()
        result = controller.close_door()
        return jsonify({
            "success": True, 
            "message": "출입문이 닫혔습니다.",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500
