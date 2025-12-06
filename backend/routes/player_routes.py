from flask import Blueprint, request, jsonify
from services.player_service import PlayerService
from services.player_statistics_service import PlayerStatisticsService

player_bp = Blueprint('players', __name__)

@player_bp.route('/players/season/<int:season_id>', methods=['GET'])
def get_players_by_season(season_id):
    """Lấy danh sách cầu thủ theo mùa (có thể lọc theo đội)"""
    try:
        team_id = request.args.get('team_id', type=int)
        
        players = PlayerStatisticsService.get_players_by_season(season_id, team_id)
        
        return jsonify({
            'status': 'success',
            'data': players
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@player_bp.route('/players/<int:player_id>/season/<int:season_id>/detailed', methods=['GET'])
def get_player_detailed_stats(player_id, season_id):
    """Lấy thông tin chi tiết của cầu thủ trong mùa"""
    try:
        player_data = PlayerStatisticsService.get_player_detailed_stats(player_id, season_id)
        
        if not player_data:
            return jsonify({
                'status': 'error',
                'message': 'Player not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': player_data
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@player_bp.route('/players', methods=['GET'])
def get_players():
    name = request.args.get('name')
    position = request.args.get('position')
    
    if name or position:
        players = PlayerService.search_players(name=name, position=position)
    else:
        players = PlayerService.get_all_players()
    
    return jsonify(players)

@player_bp.route('/players/<int:player_id>', methods=['GET'])
def get_player(player_id):
    player = PlayerService.get_player_by_id(player_id)
    if not player:
        return jsonify({'error': 'Player not found'}), 404
    return jsonify(player)

@player_bp.route('/players', methods=['POST'])
def create_player():
    data = request.json
    
    if 'full_name' not in data:
        return jsonify({'error': 'full_name is required'}), 400
    
    player = PlayerService.create_player(data)
    if player:
        return jsonify(player), 201
    return jsonify({'error': 'Failed to create player'}), 500

@player_bp.route('/players/<int:player_id>', methods=['PUT'])
def update_player(player_id):
    data = request.json
    
    player = PlayerService.update_player(player_id, data)
    if not player:
        return jsonify({'error': 'Player not found'}), 404
    
    return jsonify(player)

@player_bp.route('/players/<int:player_id>', methods=['DELETE'])
def delete_player(player_id):
    success = PlayerService.delete_player(player_id)
    if not success:
        return jsonify({'error': 'Player not found'}), 404
    return jsonify({'message': 'Player deleted successfully'}), 200