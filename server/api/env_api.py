# server/api/env_api.py
from flask import request, jsonify
from . import api_bp, controller

# ==== 환경 상태 조회 ====
@api_bp.route('/environment/status', methods=['GET'])
def get_environment_status():
    """현재 환경 상태를 조회합니다."""
    if not controller:
        return jsonify({"status": "error", "message": "컨트롤러가 초기화되지 않았습니다"}), 500
    
    result = controller.env_controller.get_status()
    return jsonify(result)

# ==== 창고별 상태 조회 ====
@api_bp.route('/environment/warehouse/<warehouse>', methods=['GET'])
def get_warehouse_status(warehouse):
    """특정 창고의 환경 상태를 조회합니다."""
    if not controller:
        return jsonify({"status": "error", "message": "컨트롤러가 초기화되지 않았습니다"}), 500
    
    # 창고 ID 검증
    if warehouse not in ['A', 'B', 'C', 'D']:
        return jsonify({"status": "error", "message": "유효하지 않은 창고 ID"}), 400
    
    result = controller.env_controller.get_warehouse_status(warehouse)
    
    if result.get("status") == "error":
        return jsonify(result), 400
    
    return jsonify(result)

# ==== 온도 설정 ====
@api_bp.route('/environment/control', methods=['PUT'])
def set_environment_control():
    """창고 온도 제어 설정을 변경합니다."""
    if not controller:
        return jsonify({"status": "error", "message": "컨트롤러가 초기화되지 않았습니다"}), 500
    
    data = request.json
    
    # 필수 파라미터 확인
    if not data or 'warehouse' not in data or 'target_temp' not in data:
        return jsonify({
            "status": "error",
            "message": "필수 파라미터 누락: warehouse, target_temp"
        }), 400
    
    warehouse = data['warehouse']
    target_temp = data['target_temp']
    
    # 창고 ID 검증
    if warehouse not in ['A', 'B', 'C', 'D']:
        return jsonify({"status": "error", "message": "유효하지 않은 창고 ID"}), 400
    
    # 온도 유효성 검증
    try:
        target_temp = float(target_temp)
    except ValueError:
        return jsonify({"status": "error", "message": "온도는 숫자여야 합니다"}), 400
    
    result = controller.env_controller.set_target_temperature(warehouse, target_temp)
    
    if result.get("status") == "error":
        return jsonify(result), 400
    
    return jsonify(result)