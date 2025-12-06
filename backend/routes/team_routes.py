# routes/team_routes.py - Sửa lại như sau
from flask import Blueprint, request, jsonify
from services.team_service import TeamService

team_bp = Blueprint('teams', __name__, url_prefix='/api/teams')

@team_bp.route('', methods=['GET'])
def get_teams():
    include_stadium = request.args.get('include_stadium', '').lower() == 'true'
    name = request.args.get('name')
    city = request.args.get('city')
    
    if name or city:
        teams = TeamService.search_teams(name=name, city=city)
    else:
        teams = TeamService.get_all_teams(include_stadium=include_stadium)
    
    return jsonify(teams)

@team_bp.route('/<int:team_id>', methods=['GET'])
def get_team(team_id):
    include_stadium = request.args.get('include_stadium', '').lower() == 'true'
    
    team = TeamService.get_team_by_id(team_id, include_stadium=include_stadium)
    if not team:
        return jsonify({'error': 'Team not found'}), 404
    return jsonify(team)

@team_bp.route('/season/<int:season_id>', methods=['GET'])
def get_teams_by_season(season_id):
    """Lấy danh sách đội theo mùa với thông tin standing"""
    try:
        teams = TeamService.get_teams_by_season(season_id)
        return jsonify({
            'status': 'success',
            'data': teams
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@team_bp.route('/<int:team_id>/season/<int:season_id>', methods=['GET'])
def get_team_season_details(team_id, season_id):
    """Lấy thông tin chi tiết của đội trong mùa bao gồm players"""
    try:
        team = TeamService.get_team_season_details(team_id, season_id)
        if not team:
            return jsonify({
                'status': 'error',
                'message': 'Team not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': team
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@team_bp.route('/<int:team_id>/statistics', methods=['GET'])
def get_team_statistics(team_id):
    """Lấy thống kê của đội"""
    try:
        season_id = request.args.get('season_id', type=int)
        
        stats = TeamService.get_team_statistics(team_id, season_id)
        
        return jsonify({
            'status': 'success',
            'data': stats or {}
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# Các route POST, PUT, DELETE giữ nguyên
@team_bp.route('', methods=['POST'])
def create_team():
    data = request.json
    
    if 'name' not in data:
        return jsonify({'error': 'name is required'}), 400
    
    team = TeamService.create_team(data)
    if team:
        return jsonify(team), 201
    return jsonify({'error': 'Failed to create team'}), 500

@team_bp.route('/<int:team_id>', methods=['PUT'])
def update_team(team_id):
    data = request.json
    
    team = TeamService.update_team(team_id, data)
    if not team:
        return jsonify({'error': 'Team not found'}), 404
    
    return jsonify(team)

@team_bp.route('/<int:team_id>', methods=['DELETE'])
def delete_team(team_id):
    success = TeamService.delete_team(team_id)
    if not success:
        return jsonify({'error': 'Team not found'}), 404
    return jsonify({'message': 'Team deleted successfully'}), 200