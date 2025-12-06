from flask import Blueprint, request, jsonify
from services.referee_service import RefereeService

referee_bp = Blueprint('referees', __name__)

@referee_bp.route('/referees', methods=['GET'])
def get_referees():
    referees = RefereeService.get_all_referees()
    return jsonify(referees)

@referee_bp.route('/referees/<int:referee_id>', methods=['GET'])
def get_referee(referee_id):
    referee = RefereeService.get_referee_by_id(referee_id)
    if not referee:
        return jsonify({'error': 'Referee not found'}), 404
    return jsonify(referee)

@referee_bp.route('/referees', methods=['POST'])
def create_referee():
    data = request.json
    
    if 'full_name' not in data:
        return jsonify({'error': 'full_name is required'}), 400
    
    referee = RefereeService.create_referee(data)
    if referee:
        return jsonify(referee), 201
    return jsonify({'error': 'Failed to create referee'}), 500

@referee_bp.route('/referees/<int:referee_id>', methods=['PUT'])
def update_referee(referee_id):
    data = request.json
    
    if 'full_name' not in data:
        return jsonify({'error': 'full_name is required'}), 400
    
    referee = RefereeService.update_referee(referee_id, data)
    if not referee:
        return jsonify({'error': 'Referee not found'}), 404
    
    return jsonify(referee)

@referee_bp.route('/referees/<int:referee_id>', methods=['DELETE'])
def delete_referee(referee_id):
    success = RefereeService.delete_referee(referee_id)
    if not success:
        return jsonify({'error': 'Referee not found'}), 404
    return jsonify({'message': 'Referee deleted successfully'}), 200