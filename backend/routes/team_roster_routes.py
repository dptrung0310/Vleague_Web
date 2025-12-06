from flask import Blueprint, request, jsonify
from services.team_roster_service import TeamRosterService

team_roster_bp = Blueprint('team_rosters', __name__)

@team_roster_bp.route('/team-rosters', methods=['GET'])
def get_rosters():
    team_id = request.args.get('team_id', type=int)
    player_id = request.args.get('player_id', type=int)
    season_id = request.args.get('season_id', type=int)
    
    if team_id and season_id:
        rosters = TeamRosterService.get_rosters_by_team(team_id, season_id)
    elif team_id:
        rosters = TeamRosterService.get_rosters_by_team(team_id)
    elif player_id:
        rosters = TeamRosterService.get_rosters_by_player(player_id)
    elif season_id:
        rosters = TeamRosterService.get_rosters_by_season(season_id)
    else:
        rosters = TeamRosterService.get_all_rosters()
    
    return jsonify(rosters)

@team_roster_bp.route('/team-rosters/<int:roster_id>', methods=['GET'])
def get_roster(roster_id):
    roster = TeamRosterService.get_roster_by_id(roster_id)
    if not roster:
        return jsonify({'error': 'Roster not found'}), 404
    return jsonify(roster)

@team_roster_bp.route('/team-rosters', methods=['POST'])
def create_roster():
    data = request.json
    
    required_fields = ['player_id', 'team_id', 'season_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    roster = TeamRosterService.create_roster(data)
    if roster:
        return jsonify(roster), 201
    return jsonify({'error': 'Failed to create roster'}), 500

@team_roster_bp.route('/team-rosters/<int:roster_id>', methods=['PUT'])
def update_roster(roster_id):
    data = request.json
    
    roster = TeamRosterService.update_roster(roster_id, data)
    if not roster:
        return jsonify({'error': 'Roster not found'}), 404
    
    return jsonify(roster)

@team_roster_bp.route('/team-rosters/<int:roster_id>', methods=['DELETE'])
def delete_roster(roster_id):
    success = TeamRosterService.delete_roster(roster_id)
    if not success:
        return jsonify({'error': 'Roster not found'}), 404
    return jsonify({'message': 'Roster deleted successfully'}), 200