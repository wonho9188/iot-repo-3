from datetime import datetime
from typing import Dict, List, Optional
from flask import Blueprint, jsonify, request

# Blueprint 초기화
router = Blueprint('expiry', __name__, url_prefix='/api/expiry')

# 컨트롤러 의존성
def get_expiry_controller():
    """유통기한 관리 컨트롤러 인스턴스를 반환합니다."""
    try:
        from server.main import init_controllers
        controllers = init_controllers()
        return controllers["expiry"]
    except ImportError:
        try:
            from main import init_controllers
            controllers = init_controllers()
            return controllers["expiry"]
        except ImportError:
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from server.main import init_controllers
            controllers = init_controllers()
            return controllers["expiry"]

@router.route("/alerts", methods=["GET"])
def get_expiry_alerts():
    """유통기한 경고 목록 조회"""
    try:
        days = request.args.get("days", default=7, type=int)
        
        controller = get_expiry_controller()
        alerts = controller.get_expiry_alerts(days)
        
        return jsonify({
            "success": True,
            "data": alerts,
            "total_count": len(alerts),
            "days_threshold": days,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@router.route("/expired", methods=["GET"])
def get_expired_items():
    """유통기한 만료 물품 목록 조회"""
    try:
        controller = get_expiry_controller()
        items = controller.get_expired_items()
        
        return jsonify({
            "success": True,
            "data": items,
            "total_count": len(items),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500 