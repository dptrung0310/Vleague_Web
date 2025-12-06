from flask import Blueprint, request, jsonify
from services.stadium_service import StadiumService

stadium_bp = Blueprint('stadiums', __name__)

@stadium_bp.route('/stadiums', methods=['GET'])
def get_stadiums():
    city = request.args.get('city')
    
    if city:
        stadiums = StadiumService.get_stadiums_by_city(city)
    else:
        stadiums = StadiumService.get_all_stadiums()
    
    return jsonify(stadiums)

@stadium_bp.route('/stadiums/<int:stadium_id>', methods=['GET'])
def get_stadium(stadium_id):
    stadium = StadiumService.get_stadium_by_id(stadium_id)
    if not stadium:
        return jsonify({'error': 'Stadium not found'}), 404
    return jsonify(stadium)

@stadium_bp.route('/stadiums', methods=['POST'])
def create_stadium():
    data = request.json
    
    required_fields = ['name', 'city']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    stadium = StadiumService.create_stadium(data)
    if stadium:
        return jsonify(stadium), 201
    return jsonify({'error': 'Failed to create stadium'}), 500

@stadium_bp.route('/stadiums/<int:stadium_id>', methods=['PUT'])
def update_stadium(stadium_id):
    data = request.json
    
    stadium = StadiumService.update_stadium(stadium_id, data)
    if not stadium:
        return jsonify({'error': 'Stadium not found'}), 404
    
    return jsonify(stadium)

@stadium_bp.route('/stadiums/<int:stadium_id>', methods=['DELETE'])
def delete_stadium(stadium_id):
    success = StadiumService.delete_stadium(stadium_id)
    if not success:
        return jsonify({'error': 'Stadium not found'}), 404
    return jsonify({'message': 'Stadium deleted successfully'}), 200