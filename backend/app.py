# app.py
from flask import Flask, jsonify, request
import subprocess
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import current_config
from extensions import db, jwt, bcrypt
import os
from flask_socketio import SocketIO, emit

def create_app():
    app = Flask(__name__)
    app.config.from_object(current_config)
    
    # Initialize extensions
    CORS(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    db.init_app(app)
    
    # QUAN TRỌNG: Khởi tạo SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*")

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
            "status": "running"
        })
    
    # Health check endpoint
    @app.route('/health')
    def health():
        return jsonify({"status": "running"})
    
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
    
    # --- API MỚI: Kích hoạt AI ---
    @app.route('/api/ai/start', methods=['POST'])
    def start_ai_process():
        data = request.json
        match_id = data.get('match_id')
        stream_url = data.get('stream_url')
        user_id = data.get('user_id') # <--- Thêm nhận user_id
        
        # CẤU HÌNH ĐƯỜNG DẪN (Sửa cho đúng máy bạn)
        AI_WORKING_DIR = r"D:\LAB\AI_Football" 
        AI_PYTHON_PATH = r"D:\LAB\AI_Football\venv_ai\Scripts\python.exe"
        AI_SCRIPT_PATH = r"run_stream_v2.py"
            
        try:
            print(f"🚀 Đang khởi động AI từ thư mục: {AI_WORKING_DIR}...")
            
            subprocess.Popen(
                [
                    AI_PYTHON_PATH, 
                    AI_SCRIPT_PATH, 
                    "--match_id", str(match_id),
                    "--url", stream_url,
                    "--user_id", str(user_id) # <--- Truyền user_id cho AI
                ],
                cwd=AI_WORKING_DIR,
                shell=True
            )
            
            return jsonify({'status': 'success', 'message': 'AI Engine started!'}), 200
        except Exception as e:
            print(f"❌ Lỗi khởi động AI: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

    # --- SOCKET HANDLERS ---
    
    @socketio.on('connect')
    def handle_connect():
        print("🔌 Client connected")

    @socketio.on('ai_card_detected')
    def handle_ai_event(data):
        print(f"🤖 AI Báo cáo thẻ: {data}")
        # Bắn tiếp tin nhắn này xuống cho Frontend
        socketio.emit('ui_update_card_count', data)

    # --- SỰ KIỆN MỚI: XỬ LÝ KẾT QUẢ CUỐI CÙNG ---
    @socketio.on('ai_finished')
    def handle_ai_finished(data):
        print(f"🏁 AI Kết thúc video: {data}")
        
        match_id = data.get('match_id')
        user_id = data.get('user_id')
        total_cards = data.get('total_cards', 0)
        
        # Cần dùng app_context để truy vấn DB trong thread socket
        with app.app_context():
            from models.prediction import Prediction
            
            # Tìm dự đoán của user
            prediction = Prediction.query.filter_by(
                user_id=user_id, 
                match_id=match_id
            ).first()
            
            if prediction and prediction.predicted_card_over_under:
                user_choice = prediction.predicted_card_over_under # 'OVER_3.5' hoặc 'UNDER_3.5'
                result_status = 'LOSE'
                
                # Logic tính thắng thua (Kèo 3.5)
                if user_choice == 'OVER_3.5':
                    if total_cards > 3.5: result_status = 'WIN'
                elif user_choice == 'UNDER_3.5':
                    if total_cards <= 3.5: result_status = 'WIN'
                
                print(f"📢 Kết quả: User {user_id} chọn {user_choice}, Thực tế {total_cards} -> {result_status}")

                # Gửi kết quả về Frontend
                socketio.emit('prediction_result', {
                    'match_id': match_id,
                    'user_id': user_id,
                    'total_cards': total_cards,
                    'result': result_status
                })

    return app, socketio