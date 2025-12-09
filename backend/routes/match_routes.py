from flask import Blueprint, request, jsonify
from services.match_service import MatchService
from models.match import Match
from extensions import db
from sqlalchemy import desc

match_bp = Blueprint('matches', __name__)

def match_to_dict(match):
    """Chuyển đổi Match object sang dictionary"""
    return {
        'match_id': match.match_id,
        'season_id': match.season_id,
        'round': match.round,
        'match_datetime': match.match_datetime.isoformat() if match.match_datetime else None,
        'home_team_id': match.home_team_id,
        'away_team_id': match.away_team_id,
        'home_score': match.home_score,
        'away_score': match.away_score,
        'status': match.status,
        'stadium_id': match.stadium_id,
        'match_url': match.match_url
    }

# match_routes.py - Cập nhật hàm get_matches
@match_bp.route('/matches', methods=['GET'])
def get_matches():
    try:
        # Lấy tham số phân trang từ query string
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Lấy tham số lọc
        season_id = request.args.get('season_id')
        round = request.args.get('round')
        status = request.args.get('status')
        
        # Debug log
        print(f"API Request - season_id: {season_id}, round: {round}, status: {status}")
        
        # Xây dựng query
        query = Match.query
        
        if season_id:
            query = query.filter(Match.season_id == season_id)
        
        if round:
            # Tìm kiếm theo vòng đấu, có thể là "Vòng 26" hoặc "26"
            # Nếu người dùng chỉ nhập số, tìm cả "Vòng {số}"
            if round:
                if round.isdigit():
                    # Chỉ tìm chính xác "Vòng {số}"
                    query = query.filter(
                        db.or_(
                            Match.round == f"Vòng {round}",
                            Match.round.like(f"Vòng {round} %"),
                            Match.round == round,
                            Match.round.like(f"{round} %")
                        )
                    )
                else:
                    query = query.filter(Match.round.like(f'%{round}%'))
        
        if status:
            query = query.filter(Match.status == status)
        
        # Sắp xếp mới nhất trước
        query = query.order_by(desc(Match.match_datetime))
        
        # Phân trang
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        print(f"Found {pagination.total} matches")
        
        # Chuyển đổi kết quả
        matches_data = []
        for match in pagination.items:
            match_dict = {
                'match_id': match.match_id,
                'season_id': match.season_id,
                'round': match.round,
                'match_datetime': match.match_datetime.isoformat() if match.match_datetime else None,
                'home_team_id': match.home_team_id,
                'away_team_id': match.away_team_id,
                'home_score': match.home_score,
                'away_score': match.away_score,
                'status': match.status,
                'stadium_id': match.stadium_id,
                'match_url': match.match_url
            }
            
            # Thêm thông tin liên quan
            if match.season:
                match_dict['season_name'] = match.season.name
            if match.home_team:
                match_dict['home_team'] = {
                    'id': match.home_team.team_id,
                    'name': match.home_team.name,
                    'logo': match.home_team.logo_url if hasattr(match.home_team, 'logo_url') else None
                }
            if match.away_team:
                match_dict['away_team'] = {
                    'id': match.away_team.team_id,
                    'name': match.away_team.name,
                    'logo': match.away_team.logo_url if hasattr(match.away_team, 'logo_url') else None
                }
            if match.stadium:
                match_dict['stadium_name'] = match.stadium.name
            
            matches_data.append(match_dict)
        
        return jsonify({
            'status': 'success',
            'data': matches_data,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }), 200
        
    except Exception as e:
        print(f"Error in get_matches: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@match_bp.route('/matches/<int:match_id>', methods=['GET'])
def get_match(match_id):
    match = MatchService.get_match_by_id(match_id)
    if not match:
        return jsonify({'error': 'Match not found'}), 404
    return jsonify(match_to_dict(match))

@match_bp.route('/matches', methods=['POST'])
def create_match():
    data = request.json
    
    # Validation đơn giản
    required_fields = ['season_id', 'match_datetime', 'home_team_id', 'away_team_id', 'stadium_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Chuyển đổi datetime string nếu cần
    if 'match_datetime' in data and isinstance(data['match_datetime'], str):
        from datetime import datetime
        try:
            data['match_datetime'] = datetime.fromisoformat(data['match_datetime'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Invalid datetime format. Use ISO format'}), 400
    
    match = MatchService.create_match(data)
    return jsonify(match_to_dict(match)), 201

@match_bp.route('/matches/<int:match_id>', methods=['PUT'])
def update_match(match_id):
    data = request.json
    
    # Chuyển đổi datetime string nếu cần
    if 'match_datetime' in data and isinstance(data['match_datetime'], str):
        from datetime import datetime
        try:
            data['match_datetime'] = datetime.fromisoformat(data['match_datetime'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Invalid datetime format. Use ISO format'}), 400
    
    match = MatchService.update_match(match_id, data)
    if not match:
        return jsonify({'error': 'Match not found'}), 404
    
    return jsonify(match_to_dict(match))

@match_bp.route('/matches/<int:match_id>', methods=['DELETE'])
def delete_match(match_id):
    success = MatchService.delete_match(match_id)
    if not success:
        return jsonify({'error': 'Match not found'}), 404
    return jsonify({'message': 'Match deleted successfully'}), 200

@match_bp.route('/matches/team/<int:team_id>', methods=['GET'])
def get_team_matches(team_id):
    matches = MatchService.get_team_matches(team_id)
    return jsonify([match_to_dict(match) for match in matches])

# Các endpoint khác cho referees, lineups, events
@match_bp.route('/matches/<int:match_id>/referees', methods=['POST'])
def add_match_referee(match_id):
    data = request.json
    
    if 'referee_id' not in data or 'role' not in data:
        return jsonify({'error': 'Missing referee_id or role'}), 400
    
    data['match_id'] = match_id
    referee = MatchService.add_match_referee(**data)
    return jsonify({
        'match_referee_id': referee.match_referee_id,
        'match_id': referee.match_id,
        'referee_id': referee.referee_id,
        'role': referee.role
    }), 201

@match_bp.route('/matches/<int:match_id>/lineups', methods=['POST'])
def add_match_lineup(match_id):
    data = request.json
    
    required_fields = ['team_id', 'player_id', 'is_starter', 'shirt_number']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    data['match_id'] = match_id
    lineup = MatchService.add_match_lineup(data)
    
    return jsonify({
        'lineup_id': lineup.lineup_id,
        'match_id': lineup.match_id,
        'team_id': lineup.team_id,
        'player_id': lineup.player_id,
        'is_starter': lineup.is_starter,
        'shirt_number': lineup.shirt_number,
        'position': lineup.position
    }), 201

@match_bp.route('/matches/<int:match_id>/events', methods=['POST'])
def add_match_event(match_id):
    data = request.json
    
    required_fields = ['team_id', 'player_id', 'event_type', 'minute']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    data['match_id'] = match_id
    event = MatchService.add_match_event(data)
    
    return jsonify({
        'event_id': event.event_id,
        'match_id': event.match_id,
        'team_id': event.team_id,
        'player_id': event.player_id,
        'event_type': event.event_type,
        'minute': event.minute
    }), 201

@match_bp.route('/matches/<int:match_id>/lineups', methods=['GET'])
def get_match_lineups(match_id):
    lineups = MatchService.get_match_lineups(match_id)
    result = []
    for lineup in lineups:
        result.append({
            'lineup_id': lineup.lineup_id,
            'match_id': lineup.match_id,
            'team_id': lineup.team_id,
            'player_id': lineup.player_id,
            'is_starter': lineup.is_starter,
            'shirt_number': lineup.shirt_number,
            'position': lineup.position
        })
    return jsonify(result)

@match_bp.route('/matches/<int:match_id>/events', methods=['GET'])
def get_match_events(match_id):
    events = MatchService.get_match_events(match_id)
    result = []
    for event in events:
        result.append({
            'event_id': event.event_id,
            'match_id': event.match_id,
            'team_id': event.team_id,
            'player_id': event.player_id,
            'event_type': event.event_type,
            'minute': event.minute
        })
    return jsonify(result)

# match_routes.py - Cập nhật endpoint get_match_details với fallback
@match_bp.route('/matches/<int:match_id>/details', methods=['GET'])
def get_match_details(match_id):
    try:
        print(f"🌐 API Request: /matches/{match_id}/details")
        
        # Thử lấy chi tiết từ service
        match_data = MatchService.get_match_with_details(match_id)
        
        if match_data:
            return jsonify({
                'status': 'success',
                'data': match_data
            }), 200
        else:
            # Thử lấy thông tin cơ bản của match
            match = Match.query.get(match_id)
            if match:
                # Tạo dữ liệu fallback từ thông tin cơ bản
                fallback_data = {
                    'match_id': match.match_id,
                    'season_id': match.season_id,
                    'round': match.round,
                    'match_datetime': match.match_datetime.isoformat() if match.match_datetime else None,
                    'home_team_id': match.home_team_id,
                    'away_team_id': match.away_team_id,
                    'home_score': match.home_score,
                    'away_score': match.away_score,
                    'status': match.status,
                    'stadium_id': match.stadium_id,
                    'match_url': match.match_url,
                    'season_name': match.season.name if match.season else None,
                    'home_team_name': match.home_team.name if match.home_team else None,
                    'away_team_name': match.away_team.name if match.away_team else None,
                    'stadium_name': match.stadium.name if match.stadium else None,
                    'events': [],  # Fallback empty
                    'lineups': [],  # Fallback empty
                    'referees': []  # Fallback empty
                }
                
                return jsonify({
                    'status': 'success',
                    'data': fallback_data,
                    'note': 'Using fallback data from basic match info'
                }), 200
            else:
                print(f"❌ API Error: Không tìm thấy match {match_id} cả basic")
                return jsonify({
                    'status': 'error',
                    'message': f'Match with ID {match_id} not found'
                }), 404
        
    except Exception as e:
        print(f"❌ API Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': 'Internal server error',
            'debug': str(e)
        }), 500