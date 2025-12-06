from flask import Blueprint, request, jsonify
from services.season_standing_service import SeasonStandingService

season_standing_bp = Blueprint('season_standings', __name__)

@season_standing_bp.route('/season-standings', methods=['GET'])
def get_standings():
    season_id = request.args.get('season_id', type=int)
    team_id = request.args.get('team_id', type=int)
    round = request.args.get('round', type=int)
    
    if season_id and round:
        standings = SeasonStandingService.get_standings_by_season(season_id, round)
    elif season_id:
        standings = SeasonStandingService.get_standings_by_season(season_id)
    elif team_id:
        standings = SeasonStandingService.get_standings_by_team(team_id)
    else:
        standings = SeasonStandingService.get_all_standings()
    
    return jsonify(standings)

@season_standing_bp.route('/season-standings/current/<int:season_id>', methods=['GET'])
def get_current_standings(season_id):
    standings = SeasonStandingService.get_current_round_standings(season_id)
    return jsonify(standings)

@season_standing_bp.route('/season-standings/<int:standing_id>', methods=['GET'])
def get_standing(standing_id):
    standing = SeasonStandingService.get_standing_by_id(standing_id)
    if not standing:
        return jsonify({'error': 'Standing not found'}), 404
    return jsonify(standing)

@season_standing_bp.route('/season-standings', methods=['POST'])
def create_standing():
    data = request.json
    
    required_fields = ['season_id', 'team_id', 'round', 'position', 'played', 
                       'wins', 'draws', 'losses', 'goals_for', 'goals_against',
                       'goal_difference', 'points']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    standing = SeasonStandingService.create_standing(data)
    if standing:
        return jsonify(standing), 201
    return jsonify({'error': 'Failed to create standing'}), 500

@season_standing_bp.route('/season-standings/<int:standing_id>', methods=['PUT'])
def update_standing(standing_id):
    data = request.json
    
    standing = SeasonStandingService.update_standing(standing_id, data)
    if not standing:
        return jsonify({'error': 'Standing not found'}), 404
    
    return jsonify(standing)

@season_standing_bp.route('/season-standings/<int:standing_id>', methods=['DELETE'])
def delete_standing(standing_id):
    success = SeasonStandingService.delete_standing(standing_id)
    if not success:
        return jsonify({'error': 'Standing not found'}), 404
    return jsonify({'message': 'Standing deleted successfully'}), 200

@season_standing_bp.route('/season-standings/details/<int:season_id>/<int:round>', methods=['GET'])
def get_standings_with_details(season_id, round):
    standings = SeasonStandingService.get_standings_with_details(season_id, round)
    return jsonify(standings)