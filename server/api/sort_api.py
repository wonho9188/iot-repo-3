# server/api/sort_api.py
from flask import request, jsonify
from . import api_bp, controller

# ==== 분류 시작 ====
@api_bp.route('/inbound/start', methods=['POST'])
def start_inbound():
    """분류기 작동을 시작합니다."""
    if not controller:
        return jsonify({"status": "error", "message": "컨트롤러가 초기화되지 않았습니다"}), 500
    
    result = controller.sort_controller.start_sorting()
    
    if result.get("status") == "error":
        return jsonify(result), 400
    
    return jsonify(result)

# ==== 분류 종료 ====
@api_bp.route('/inbound/stop', methods=['POST'])
def stop_inbound():
    """분류기 작동을 정지합니다."""
    if not controller:
        return jsonify({"status": "error", "message": "컨트롤러가 초기화되지 않았습니다"}), 500
    
    result = controller.sort_controller.stop_sorting()
    
    if result.get("status") == "error":
        return jsonify(result), 400
    
    return jsonify(result)

# ==== 비상 정지 ====
@api_bp.route('/emergency/stop', methods=['POST'])
def emergency_stop():
    """분류기를 긴급 정지합니다."""
    if not controller:
        return jsonify({"status": "error", "message": "컨트롤러가 초기화되지 않았습니다"}), 500
    
    result = controller.sort_controller.emergency_stop()
    
    if result.get("status") == "error":
        return jsonify(result), 400
    
    return jsonify(result)

# ==== 분류기 상태 조회 ====
@api_bp.route('/inbound/status', methods=['GET'])
def get_inbound_status():
    """현재 분류기 상태를 조회합니다."""
    if not controller:
        return jsonify({"status": "error", "message": "컨트롤러가 초기화되지 않았습니다"}), 500
    
    result = controller.sort_controller.get_status()
    return jsonify(result)