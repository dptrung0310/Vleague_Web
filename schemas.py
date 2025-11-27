from flask_restx import fields


def init_schemas(api):
    """
    Khởi tạo các schema (Model) cho Swagger UI.
    Bao gồm Input Model (cho POST/PUT) và Output Model (cho GET).
    """

    # --- LEAGUE SCHEMAS ---
    league_input_model = api.model('LeagueInput', {
        'name': fields.String(required=True, description='Tên giải đấu', example='V.League 1'),
        'code': fields.String(required=True, description='Mã giải đấu', example='VL1'),
        'logo_url': fields.String(description='URL Logo giải đấu', example='https://example.com/logo.png')
    })

    league_output_model = api.model('LeagueOutput', {
        'league_id': fields.Integer(description='ID giải đấu'),
        'name': fields.String(description='Tên giải đấu'),
        'code': fields.String(description='Mã giải đấu'),
        'logo_url': fields.String(description='URL Logo')
    })

    # --- SEASON SCHEMAS ---
    season_input_model = api.model('SeasonInput', {
        'league_id': fields.Integer(required=True, description='ID giải đấu thuộc về'),
        'name': fields.String(required=True, description='Tên mùa giải', example='Mùa giải 2023/2024'),
        'vpf_sid': fields.Integer(required=True, description='Mã ID từ hệ thống VPF'),
        'start_date': fields.String(description='Ngày bắt đầu (YYYY-MM-DD)', example='2023-10-01'),
        'end_date': fields.String(description='Ngày kết thúc (YYYY-MM-DD)', example='2024-06-30')
    })

    season_output_model = api.model('SeasonOutput', {
        'season_id': fields.Integer(description='ID mùa giải'),
        'league_id': fields.Integer(description='ID giải đấu'),
        'name': fields.String(description='Tên mùa giải'),
        'vpf_sid': fields.Integer(description='VPF SID'),
        'start_date': fields.String(description='Ngày bắt đầu'),
        'end_date': fields.String(description='Ngày kết thúc')
    })

    # --- REFEREE SCHEMAS ---
    referee_input_model = api.model('RefereeInput', {
        'full_name': fields.String(required=True, description='Họ và tên trọng tài', example='Ngô Duy Lân')
    })

    referee_output_model = api.model('RefereeOutput', {
        'referee_id': fields.Integer(description='ID trọng tài'),
        'full_name': fields.String(description='Họ và tên trọng tài')
    })

    # --- STADIUM SCHEMAS ---
    stadium_input_model = api.model('StadiumInput', {
        'name': fields.String(required=True, description='Tên sân vận động', example='Sân vận động Mỹ Đình'),
        'city': fields.String(required=True, description='Thành phố', example='Hà Nội'),
        'address': fields.String(description='Địa chỉ cụ thể'),
        'latitude': fields.Float(description='Vĩ độ'),
        'longitude': fields.Float(description='Kinh độ')
    })

    stadium_output_model = api.model('StadiumOutput', {
        'stadium_id': fields.Integer(description='ID sân'),
        'name': fields.String(description='Tên sân'),
        'city': fields.String(description='Thành phố'),
        'address': fields.String(description='Địa chỉ'),
        'latitude': fields.Float(description='Vĩ độ'),
        'longitude': fields.Float(description='Kinh độ')
    })

    # --- MATCH SCHEMAS ---
    match_input_model = api.model('MatchInput', {
        'season_id': fields.Integer(required=True, description='ID mùa giải'),
        'round': fields.String(description='Vòng đấu', example='Vòng 1'),
        'match_datetime': fields.String(description='Thời gian đá (YYYY-MM-DD HH:MM:SS)',
                                        example='2023-10-25 18:00:00'),
        'home_team_id': fields.Integer(required=True, description='ID đội nhà'),
        'away_team_id': fields.Integer(required=True, description='ID đội khách'),
        'stadium_id': fields.Integer(required=True, description='ID sân vận động'),
        'home_score': fields.Integer(description='Bàn thắng đội nhà'),
        'away_score': fields.Integer(description='Bàn thắng đội khách'),
        'status': fields.String(description='Trạng thái', example='Finished'),
        'match_url': fields.String(description='Link xem trận đấu')
    })

    match_output_model = api.model('MatchOutput', {
        'match_id': fields.Integer(description='ID trận đấu'),
        'season_id': fields.Integer(description='ID mùa giải'),
        'round': fields.String(description='Vòng đấu'),
        'match_datetime': fields.String(description='Thời gian'),
        'home_team_id': fields.Integer(description='ID đội nhà'),
        'away_team_id': fields.Integer(description='ID đội khách'),
        'home_score': fields.Integer(description='Tỉ số nhà'),
        'away_score': fields.Integer(description='Tỉ số khách'),
        'stadium_id': fields.Integer(description='ID sân'),
        'status': fields.String(description='Trạng thái')
    })

    # --- MATCH EVENT SCHEMAS ---
    event_input_model = api.model('MatchEventInput', {
        'match_id': fields.Integer(required=True, description='ID trận đấu'),
        'team_id': fields.Integer(required=True, description='ID đội bóng'),
        'player_id': fields.Integer(required=True, description='ID cầu thủ'),
        'event_type': fields.String(required=True, description='Loại sự kiện (Goal, Card...)', example='Goal'),
        'minute': fields.Integer(required=True, description='Phút diễn ra', example=45)
    })

    event_output_model = api.model('MatchEventOutput', {
        'event_id': fields.Integer(description='ID sự kiện'),
        'match_id': fields.Integer(description='ID trận đấu'),
        'event_type': fields.String(description='Loại sự kiện'),
        'minute': fields.Integer(description='Phút')
    })

    # --- MATCH LINEUP SCHEMAS ---
    lineup_input_model = api.model('MatchLineupInput', {
        'match_id': fields.Integer(required=True),
        'team_id': fields.Integer(required=True),
        'player_id': fields.Integer(required=True),
        'is_starter': fields.Boolean(description='Đá chính hay dự bị', default=False),
        'shirt_number': fields.Integer(required=True, description='Số áo'),
        'position': fields.String(description='Vị trí', example='GK')
    })

    lineup_output_model = api.model('MatchLineupOutput', {
        'lineup_id': fields.Integer(),
        'player_id': fields.Integer(),
        'is_starter': fields.Boolean(),
        'shirt_number': fields.Integer(),
        'position': fields.String()
    })

    # --- MATCH REFEREE SCHEMAS ---
    match_referee_input_model = api.model('MatchRefereeInput', {
        'match_id': fields.Integer(required=True),
        'referee_id': fields.Integer(required=True),
        'role': fields.String(required=True, description='Vai trò (Main, Assistant, VAR)', example='Main')
    })

    match_referee_output_model = api.model('MatchRefereeOutput', {
        'match_referee_id': fields.Integer(),
        'referee_id': fields.Integer(),
        'role': fields.String()
    })

    # --- TEAM MATCH STAT SCHEMAS ---
    stat_input_model = api.model('TeamMatchStatInput', {
        'match_id': fields.Integer(required=True),
        'team_id': fields.Integer(required=True),
        'possession_percentage': fields.Integer(description='Tỉ lệ kiểm soát bóng (%)'),
        'shots_on_target': fields.Integer(),
        'shots_off_target': fields.Integer(),
        'corners': fields.Integer(),
        'offsides': fields.Integer(),
        'fouls': fields.Integer(),
        'yellow_cards': fields.Integer(),
        'red_cards': fields.Integer()
    })

    stat_output_model = api.model('TeamMatchStatOutput', {
        'stat_id': fields.Integer(),
        'match_id': fields.Integer(),
        'team_id': fields.Integer(),
        'possession_percentage': fields.Integer(),
        'shots_on_target': fields.Integer(),
        'corners': fields.Integer()
    })

    # --- TEAM SCHEMAS ---
    team_input_model = api.model('TeamInput', {
        'name': fields.String(required=True, description='Tên đội bóng', example='Hà Nội FC'),
        'logo_url': fields.String(description='Logo URL'),
        'home_stadium_id': fields.Integer(description='ID sân nhà')
    })

    team_output_model = api.model('TeamOutput', {
        'team_id': fields.Integer(description='ID đội bóng'),
        'name': fields.String(description='Tên đội'),
        'logo_url': fields.String(description='Logo URL'),
        'home_stadium_id': fields.Integer(description='ID sân nhà')
    })

    # --- PLAYER SCHEMAS ---
    player_input_model = api.model('PlayerInput', {
        'full_name': fields.String(required=True, description='Họ tên cầu thủ', example='Nguyễn Quang Hải'),
        'birth_date': fields.String(description='Ngày sinh (YYYY-MM-DD)', example='1997-04-12'),
        'height_cm': fields.Integer(description='Chiều cao (cm)'),
        'weight_kg': fields.Integer(description='Cân nặng (kg)'),
        'position': fields.String(description='Vị trí sở trường', example='MF'),
        'image_url': fields.String(description='Ảnh đại diện')
    })

    player_output_model = api.model('PlayerOutput', {
        'player_id': fields.Integer(description='ID cầu thủ'),
        'full_name': fields.String(description='Họ tên'),
        'birth_date': fields.String(description='Ngày sinh'),
        'height_cm': fields.Integer(description='Chiều cao'),
        'weight_kg': fields.Integer(description='Cân nặng'),
        'position': fields.String(description='Vị trí'),
        'image_url': fields.String(description='Ảnh đại diện')
    })

    # --- TEAM ROSTER SCHEMAS ---
    roster_input_model = api.model('TeamRosterInput', {
        'player_id': fields.Integer(required=True, description='ID cầu thủ'),
        'team_id': fields.Integer(required=True, description='ID đội bóng'),
        'season_id': fields.Integer(required=True, description='ID mùa giải'),
        'shirt_number': fields.Integer(required=True, description='Số áo thi đấu', example=19)
    })

    roster_output_model = api.model('TeamRosterOutput', {
        'roster_id': fields.Integer(description='ID danh sách'),
        'player_id': fields.Integer(),
        'team_id': fields.Integer(),
        'season_id': fields.Integer(),
        'shirt_number': fields.Integer()
    })

    # --- TRANSFER SCHEMAS ---
    transfer_input_model = api.model('TransferInput', {
        'player_id': fields.Integer(required=True, description='ID cầu thủ'),
        'from_team_id': fields.Integer(description='ID đội đi (Null nếu tự do)'),
        'to_team_id': fields.Integer(required=True, description='ID đội đến'),
        'season_id': fields.Integer(description='ID mùa giải diễn ra chuyển nhượng'),
        'transfer_date': fields.String(description='Ngày chuyển nhượng (YYYY-MM-DD)', example='2023-06-01'),
        'transfer_type': fields.String(description='Loại chuyển nhượng (buy, loan, free)', example='buy'),
        'transfer_fee': fields.Float(description='Phí chuyển nhượng (tỷ VNĐ)', example=5.5)
    })

    transfer_output_model = api.model('TransferOutput', {
        'transfer_id': fields.Integer(),
        'player_id': fields.Integer(),
        'from_team_id': fields.Integer(),
        'to_team_id': fields.Integer(),
        'season_id': fields.Integer(),
        'transfer_date': fields.String(),
        'transfer_type': fields.String(),
        'transfer_fee': fields.Float()
    })

    # --- ARTICLE SCHEMAS ---
    article_input_model = api.model('ArticleInput', {
        'title': fields.String(required=True, description='Tiêu đề bài viết', example='Kết quả vòng 5 V.League'),
        'slug': fields.String(description='URL thân thiện (để trống sẽ tự sinh)', example='ket-qua-vong-5-vleague'),
        'content': fields.String(required=True, description='Nội dung bài viết (HTML hoặc Text)'),
        'thumbnail_url': fields.String(description='Link ảnh thumbnail'),
        'related_match_id': fields.Integer(description='ID trận đấu liên quan (nếu có)'),
        # author_id thường lấy từ token của người đang đăng nhập
    })

    article_output_model = api.model('ArticleOutput', {
        'article_id': fields.Integer(),
        'title': fields.String(),
        'slug': fields.String(),
        'content': fields.String(),
        'thumbnail_url': fields.String(),
        'author_id': fields.Integer(),
        'created_at': fields.String(),
        'related_match_id': fields.Integer()
    })

    # --- USER & AUTH SCHEMAS ---
    user_register_model = api.model('UserRegister', {
        'username': fields.String(required=True, min_length=3, example='admin_user'),
        'email': fields.String(required=True, example='admin@example.com'),
        'password': fields.String(required=True, min_length=6, example='password123'),
        'role': fields.String(description='Vai trò (user, editor, admin)', default='user')
    })

    user_update_model = api.model('UserUpdate', {
        'email': fields.String(description='Email mới'),
        'password': fields.String(description='Mật khẩu mới (nếu muốn đổi)'),
        'role': fields.String(description='Vai trò')
    })

    user_output_model = api.model('UserOutput', {
        'user_id': fields.Integer(),
        'username': fields.String(),
        'email': fields.String(),
        'role': fields.String(),
        'created_at': fields.String()
    })

    login_input_model = api.model('LoginInput', {
        'username': fields.String(required=True, description='Username hoặc Email'),
        'password': fields.String(required=True)
    })

    auth_response_model = api.model('AuthResponse', {
        'message': fields.String(),
        'access_token': fields.String(),
        'refresh_token': fields.String(),
        'user': fields.Nested(user_output_model)
    })

    # --- STANDING SCHEMAS ---
    standing_input_model = api.model('StandingInput', {
        'season_id': fields.Integer(required=True),
        'team_id': fields.Integer(required=True),
        'round': fields.Integer(required=True, description='Vòng đấu số mấy'),
        'wins': fields.Integer(required=True, min=0),
        'draws': fields.Integer(required=True, min=0),
        'losses': fields.Integer(required=True, min=0),
        'goals_for': fields.Integer(required=True, min=0),
        'goals_against': fields.Integer(required=True, min=0),
        'position': fields.Integer(description='Thứ hạng tạm tính (nếu cần)')
    })

    standing_output_model = api.model('StandingOutput', {
        'standing_id': fields.Integer(),
        'season_id': fields.Integer(),
        'team_id': fields.Integer(),
        'round': fields.Integer(),
        'position': fields.Integer(),
        'played': fields.Integer(),
        'wins': fields.Integer(),
        'draws': fields.Integer(),
        'losses': fields.Integer(),
        'goals_for': fields.Integer(),
        'goals_against': fields.Integer(),
        'goal_difference': fields.Integer(),
        'points': fields.Integer()
    })

    return {
        'league_input': league_input_model,
        'league_output': league_output_model,
        'season_input': season_input_model,
        'season_output': season_output_model,
        'referee_input': referee_input_model,
        'referee_output': referee_output_model,
        'stadium_input': stadium_input_model,
        'stadium_output': stadium_output_model,

        'match_input': match_input_model,
        'match_output': match_output_model,
        'event_input': event_input_model,
        'event_output': event_output_model,
        'lineup_input': lineup_input_model,
        'lineup_output': lineup_output_model,
        'match_referee_input': match_referee_input_model,
        'match_referee_output': match_referee_output_model,
        'stat_input': stat_input_model,
        'stat_output': stat_output_model,

        'team_input': team_input_model,
        'team_output': team_output_model,
        'player_input': player_input_model,
        'player_output': player_output_model,
        'roster_input': roster_input_model,
        'roster_output': roster_output_model,
        'transfer_input': transfer_input_model,
        'transfer_output': transfer_output_model,

        'article_input': article_input_model,
        'article_output': article_output_model,
        'user_register': user_register_model,
        'user_update': user_update_model,
        'user_output': user_output_model,
        'login_input': login_input_model,
        'auth_response': auth_response_model,
        'standing_input': standing_input_model,
        'standing_output': standing_output_model
    }