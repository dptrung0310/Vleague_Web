from flask import Blueprint, request, jsonify
from services.season_service import SeasonService
from models.season import Season

season_bp = Blueprint('seasons', __name__)

@season_bp.route('', methods=['GET'])
def get_seasons():
    try:
        # Lấy tất cả seasons, sắp xếp theo start_date giảm dần (mới nhất trước)
        seasons = Season.query.order_by(Season.start_date.desc()).all()
        
        seasons_data = []
        for season in seasons:
            seasons_data.append({
                'season_id': season.season_id,
                'name': season.name,
                'start_date': season.start_date.isoformat() if season.start_date else None,
                'end_date': season.end_date.isoformat() if season.end_date else None,
                'vpf_sid': season.vpf_sid
            })
        
        return jsonify({
            'status': 'success',
            'data': seasons_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    
@season_bp.route('/seasons/current', methods=['GET'])
def get_current_season():
    season = SeasonService.get_current_season()
    if not season:
        return jsonify({'error': 'No current season found'}), 404
    return jsonify(season)

@season_bp.route('/seasons/<int:season_id>', methods=['GET'])
def get_season(season_id):
    season = SeasonService.get_season_by_id(season_id)
    if not season:
        return jsonify({'error': 'Season not found'}), 404
    return jsonify(season)

@season_bp.route('/seasons', methods=['POST'])
def create_season():
    data = request.json
    
    required_fields = ['season_id', 'name', 'vpf_sid']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    season = SeasonService.create_season(data)
    if season:
        return jsonify(season), 201
    return jsonify({'error': 'Failed to create season'}), 500

@season_bp.route('/seasons/<int:season_id>', methods=['PUT'])
def update_season(season_id):
    data = request.json
    
    season = SeasonService.update_season(season_id, data)
    if not season:
        return jsonify({'error': 'Season not found'}), 404
    
    return jsonify(season)

@season_bp.route('/seasons/<int:season_id>', methods=['DELETE'])
def delete_season(season_id):
    success = SeasonService.delete_season(season_id)
    if not success:
        return jsonify({'error': 'Season not found'}), 404
    return jsonify({'message': 'Season deleted successfully'}), 200