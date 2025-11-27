from flask import Flask
from flask_cors import CORS
from flask_restx import Api

from extensions import jwt, db, cache, bcrypt
from config import Config

from routes.core_routes import init_league_routes, init_season_routes, init_referee_routes, init_stadium_routes
from routes.match_routes import init_match_routes, init_match_lineup_routes, init_match_referee_routes, \
    init_match_event_routes, init_team_match_stat_routes
from routes.standing_route import init_season_standing_routes
from routes.system_routes import init_article_routes, init_user_routes
from routes.team_player_routes import init_team_routes, init_player_routes, init_team_roster_routes, \
    init_transfer_routes

# Import schemas init
from schemas import init_schemas

def create_app():
    app = Flask(__name__)

    # Cấu hình CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173"], # URL Frontend của bạn
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    app.config.from_object(Config)

    # Khởi tạo Swagger API
    api = Api(
        app,
        version="1.0",
        title="Soccer League Management API",
        description="API quản lý giải đấu bóng đá, tự động sinh document",
        doc="/docs/",
        authorizations=Config.AUTHORIZATIONS,
        security=None # Mặc định không khóa, endpoint nào cần thì thêm @jwt_required
    )

    # Tạo các Namespaces
    league_ns = api.namespace("Leagues", path="/api/leagues", description="Quản lý Giải đấu")
    season_ns = api.namespace("Seasons", path="/api/seasons", description="Quản lý Mùa giải")
    referee_ns = api.namespace("Referees", path="/api/referees", description="Quản lý Trọng tài")
    stadium_ns = api.namespace("Stadiums", path="/api/stadiums", description="Quản lý Sân vận động")

    match_ns = api.namespace("Matches", path="/api/matches", description="Quản lý Trận đấu")
    lineup_ns = api.namespace("MatchLineups", path="/api/match-lineups", description="Quản lý Đội hình ra sân")
    match_ref_ns = api.namespace("MatchReferees", path="/api/match-referees", description="Quản lý Trọng tài trận đấu")
    event_ns = api.namespace("MatchEvents", path="/api/match-events", description="Quản lý Sự kiện trận đấu")
    stat_ns = api.namespace("MatchStats", path="/api/match-stats", description="Quản lý Thống kê trận đấu")

    team_ns = api.namespace("Teams", path="/api/teams", description="Quản lý Đội bóng")
    player_ns = api.namespace("Players", path="/api/players", description="Quản lý Cầu thủ")
    roster_ns = api.namespace("Rosters", path="/api/rosters", description="Quản lý Danh sách đăng ký thi đấu")
    transfer_ns = api.namespace("Transfers", path="/api/transfers", description="Quản lý Chuyển nhượng")

    article_ns = api.namespace("Articles", path="/api/articles", description="Quản lý Tin tức & Bài viết")
    user_ns = api.namespace("Users", path="/api/users", description="Hệ thống Người dùng & Xác thực")
    standing_ns = api.namespace("Standings", path="/api/standings", description="Bảng xếp hạng")

    # Khởi tạo Extensions
    db.init_app(app)
    jwt.init_app(app)
    cache.init_app(app) # Bỏ comment nếu dùng cache
    bcrypt.init_app(app) # Bỏ comment nếu dùng bcrypt

    # Khởi tạo Schemas (Models cho Swagger)
    schemas = init_schemas(api)

    # Đăng ký Routes và inject dependency
    init_league_routes(api, league_ns, schemas)
    init_season_routes(api, season_ns, schemas)
    init_referee_routes(api, referee_ns, schemas)
    init_stadium_routes(api, stadium_ns, schemas)

    init_match_routes(api, match_ns, schemas)
    init_match_lineup_routes(api, lineup_ns, schemas)
    init_match_referee_routes(api, match_ref_ns, schemas)
    init_match_event_routes(api, event_ns, schemas)
    init_team_match_stat_routes(api, stat_ns, schemas)

    init_team_routes(api, team_ns, schemas)
    init_player_routes(api, player_ns, schemas)
    init_team_roster_routes(api, roster_ns, schemas)
    init_transfer_routes(api, transfer_ns, schemas)

    init_article_routes(api, article_ns, schemas)
    init_user_routes(api, user_ns, schemas)
    init_season_standing_routes(api, standing_ns, schemas)

    # Tạo database tables (chỉ dùng cho dev/test)
    with app.app_context():
        db.create_all()

    @app.route('/health')
    def health_check():
        return {"status": "OK", "message": "Soccer API is running!"}

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)