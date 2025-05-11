from datetime import datetime
from typing import Dict, List, Optional
from flask import Blueprint, jsonify, request

# Blueprint 초기화
router = Blueprint('inventory', __name__, url_prefix='/api/inventory')

# 컨트롤러 의존성
def get_inventory_controller():
    """재고 관리 컨트롤러 인스턴스를 반환합니다."""
    try:
        from server.main import init_controllers
        controllers = init_controllers()
        return controllers["inventory"]
    except ImportError:
        try:
            from main import init_controllers
            controllers = init_controllers()
            return controllers["inventory"]
        except ImportError:
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from server.main import init_controllers
            controllers = init_controllers()
            return controllers["inventory"]

@router.route("/status", methods=["GET"])
def get_inventory_status():
    """재고 상태 조회"""
    try:
        controller = get_inventory_controller()
        status = controller.get_inventory_status()
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

@router.route("/items", methods=["GET"])
def get_inventory_items():
    """재고 물품 목록 조회"""
    try:
        category = request.args.get("category")
        limit = request.args.get("limit", default=20, type=int)
        offset = request.args.get("offset", default=0, type=int)
        
        controller = get_inventory_controller()
        items = controller.get_inventory_items(category, limit, offset)
        
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

@router.route("/items/<item_id>", methods=["GET"])
def get_inventory_item(item_id):
    """재고 물품 상세 조회"""
    try:
        controller = get_inventory_controller()
        item = controller.get_inventory_item(item_id)
        
        if not item:
            return jsonify({
                "success": False,
                "error": "물품을 찾을 수 없습니다.",
                "timestamp": datetime.now().isoformat()
            }), 404
            
        return jsonify({
            "success": True,
            "data": item,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500 