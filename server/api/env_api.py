from datetime import datetime
from typing import Dict, Optional
from flask import Blueprint, jsonify, request

# Blueprint 초기화
router = Blueprint('environment', __name__, url_prefix='/api/environment')

# 컨트롤러 의존성
def get_env_controller():
    """환경 제어 컨트롤러 인스턴스를 반환합니다."""
    try:
        from server.main import init_controllers
        controllers = init_controllers()
        return controllers["env"]
    except ImportError:
        try:
            from main import init_controllers
            controllers = init_controllers()
            return controllers["env"]
        except ImportError:
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from server.main import init_controllers
            controllers = init_controllers()
            return controllers["env"]

@router.route("/set-temperature", methods=["POST"])
def set_temperature():
    """온도 설정"""
    try:
        data = request.json
        warehouse = data.get("warehouse")
        temperature = data.get("temperature")
        
        if not warehouse or temperature is None:
            return jsonify({"success": False, "error": "창고와 온도를 지정해야 합니다."}), 400
        
        controller = get_env_controller()
        result = controller.set_temperature(warehouse, temperature)
        return jsonify({
            "success": True, 
            "message": f"{warehouse} 창고 온도가 {temperature}로 설정되었습니다."
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@router.route("/status", methods=["GET"])
def get_environment_status():
    """환경 상태 조회"""
    try:
        controller = get_env_controller()
        status = controller.get_environment_status()
        return jsonify({
            "success": True,
            "data": status,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@router.route("/history", methods=["GET"])
def get_temperature_history():
    """온도 히스토리 조회"""
    try:
        warehouse = request.args.get("warehouse")
        hours = request.args.get("hours", default=24, type=int)
        
        if not warehouse:
            return jsonify({"success": False, "error": "창고 ID를 지정해야 합니다."}), 400
            
        controller = get_env_controller()
        history = controller.get_temperature_history(warehouse, hours)
        
        return jsonify({
            "success": True,
            "warehouse": warehouse,
            "data": history,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500
