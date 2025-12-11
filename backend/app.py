# app.py
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import current_config
from extensions import db, jwt, bcrypt
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(current_config)
    
    # Initialize extensions
    CORS(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    db.init_app(app)
    
    # Import và register blueprints
    from routes import (
        player_bp, referee_bp, season_bp,
        stadium_bp, team_bp, match_bp,
        team_roster_bp, season_standing_bp, user_bp, prediction_bp,
        post_bp, like_bp, comment_bp, user_achievement_bp,
        achievement_bp
    )

    # Register blueprints
    app.register_blueprint(player_bp, url_prefix='/api')
    app.register_blueprint(referee_bp, url_prefix='/api')
    app.register_blueprint(season_bp, url_prefix='/api/seasons')
    app.register_blueprint(stadium_bp, url_prefix='/api')
    app.register_blueprint(team_bp)
    app.register_blueprint(match_bp, url_prefix='/api')
    app.register_blueprint(team_roster_bp, url_prefix='/api')      
    app.register_blueprint(season_standing_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/api/auth')
    app.register_blueprint(prediction_bp, url_prefix='/api')
    app.register_blueprint(post_bp, url_prefix='/api/posts')
    app.register_blueprint(like_bp, url_prefix='/api')
    app.register_blueprint(comment_bp, url_prefix='/api')
    app.register_blueprint(user_achievement_bp, url_prefix='/api')
    app.register_blueprint(achievement_bp, url_prefix='/api')
    
    # Root endpoint
    @app.route('/')
    def root():
        return jsonify({
            "message": "Football Social Network API",
            "version": "1.0",
            "description": "API cho mạng xã hội bóng đá",
            "authentication": {
                "register": "POST /api/auth/register",
                "login": "POST /api/auth/login",
                "refresh": "POST /api/auth/refresh",
                "profile": "GET /api/users/me"
            },
            "example_request": {
                "login": {
                    "url": "POST /api/auth/login",
                    "body": '{"email": "user@example.com", "password": "your_password"}'
                }
            }
        })
    
    # Health check endpoint
    @app.route('/health')
    def health():
        try:
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            db_status = "connected"
        except Exception as e:
            db_status = f"disconnected: {str(e)}"
        
        from datetime import datetime
        return jsonify({
            "status": "running",
            "database": db_status,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0"
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "message": "Không tìm thấy trang"
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "success": False,
            "message": "Lỗi server"
        }), 500
    
    # Create database tables on startup
    with app.app_context():
        try:
            from models import (
                User, Post, Comment, Like, Achievement, UserAchievement,
                Prediction, Team, Player, Match, Season, Stadium, Referee,
                TeamRoster, SeasonStanding, MatchLineup, MatchEvent, MatchReferee
            )
            db.create_all()
            print("✓ Database tables created successfully")
        except Exception as e:
            print(f"✗ Error creating database tables: {e}")
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)