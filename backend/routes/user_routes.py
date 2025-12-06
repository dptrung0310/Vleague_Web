# routes/user_routes.py
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from services.user_service import UserService
import re
import os
import requests
from urllib.parse import urlencode

user_bp = Blueprint('user', __name__)

# ==================== GOOGLE OAUTH ====================

@user_bp.route('/auth/google', methods=['GET'])
def google_login_url():
    """Tạo URL đăng nhập Google"""
    try:
        # Cấu hình Google OAuth
        google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        params = {
            'client_id': os.environ.get('GOOGLE_CLIENT_ID', ''),
            'redirect_uri': os.environ.get('GOOGLE_REDIRECT_URI', 'http://localhost:3000/auth/google/callback'),
            'response_type': 'code',
            'scope': 'openid email profile',
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        auth_url = f"{google_auth_url}?{urlencode(params)}"
        
        return jsonify({
            'success': True,
            'data': {
                'auth_url': auth_url
            }
        }), 200
        
    except Exception as e:
        print(f"ERROR in google_login_url: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Lỗi khi tạo URL đăng nhập Google'
        }), 500

@user_bp.route('/auth/google/callback', methods=['POST'])
def google_callback():
    """Xử lý callback từ Google OAuth"""
    try:
        data = request.get_json()
        code = data.get('code')
        
        if not code:
            return jsonify({
                'success': False,
                'message': 'Thiếu mã xác thực'
            }), 400
        
        # Lấy access token từ Google
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            'code': code,
            'client_id': os.environ.get('GOOGLE_CLIENT_ID', ''),
            'client_secret': os.environ.get('GOOGLE_CLIENT_SECRET', ''),
            'redirect_uri': os.environ.get('GOOGLE_REDIRECT_URI', 'http://localhost:3000/auth/google/callback'),
            'grant_type': 'authorization_code'
        }
        
        token_response = requests.post(token_url, data=token_data)
        token_json = token_response.json()
        
        if 'access_token' not in token_json:
            return jsonify({
                'success': False,
                'message': 'Không thể lấy access token từ Google'
            }), 400
        
        # Lấy thông tin user từ Google
        userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {'Authorization': f'Bearer {token_json["access_token"]}'}
        userinfo_response = requests.get(userinfo_url, headers=headers)
        userinfo = userinfo_response.json()
        
        # Kiểm tra email
        if 'email' not in userinfo:
            return jsonify({
                'success': False,
                'message': 'Không thể lấy email từ Google'
            }), 400
        
        email = userinfo['email']
        google_id = userinfo.get('id', '')
        name = userinfo.get('name', '')
        picture = userinfo.get('picture', '')
        
        # Kiểm tra xem user đã tồn tại chưa
        from extensions import db
        from sqlalchemy import text
        
        # Kiểm tra trong bảng GoogleAuth
        query = text('''
            SELECT u.user_id, u.username, u.email, u.full_name, u.avatar_url,
                   u.points, u.correct_predictions, u.total_predictions
            FROM Users u
            JOIN GoogleAuth ga ON u.user_id = ga.user_id
            WHERE ga.google_id = :google_id OR u.email = :email
        ''')
        
        result = db.session.execute(query, {
            'google_id': google_id,
            'email': email
        }).fetchone()
        
        if result:
            # User đã tồn tại, tạo JWT token
            user_dict = dict(result._mapping)
            
            # Cập nhật avatar nếu có
            if picture and not user_dict.get('avatar_url'):
                update_query = text('''
                    UPDATE Users SET avatar_url = :avatar_url WHERE user_id = :user_id
                ''')
                db.session.execute(update_query, {
                    'avatar_url': picture,
                    'user_id': user_dict['user_id']
                })
                db.session.commit()
                user_dict['avatar_url'] = picture
        else:
            # Tạo user mới
            # Tạo username từ email
            username = email.split('@')[0]
            
            # Kiểm tra username trùng
            counter = 1
            original_username = username
            while True:
                check_query = text('SELECT COUNT(*) as count FROM Users WHERE username = :username')
                check_result = db.session.execute(check_query, {'username': username}).fetchone()
                if check_result and check_result.count == 0:
                    break
                username = f"{original_username}{counter}"
                counter += 1
            
            # Tạo user
            user_query = text('''
                INSERT INTO Users (username, email, full_name, avatar_url)
                VALUES (:username, :email, :full_name, :avatar_url)
            ''')
            
            db.session.execute(user_query, {
                'username': username,
                'email': email,
                'full_name': name,
                'avatar_url': picture
            })
            db.session.commit()
            
            # Lấy user_id vừa tạo
            last_id = db.session.execute(text('SELECT last_insert_rowid()')).fetchone()[0]
            
            # Thêm vào GoogleAuth
            google_auth_query = text('''
                INSERT INTO GoogleAuth (user_id, google_id, email)
                VALUES (:user_id, :google_id, :email)
            ''')
            
            db.session.execute(google_auth_query, {
                'user_id': last_id,
                'google_id': google_id,
                'email': email
            })
            db.session.commit()
            
            # Lấy thông tin user
            user_query = text('''
                SELECT user_id, username, email, full_name, avatar_url,
                       points, correct_predictions, total_predictions
                FROM Users WHERE user_id = :user_id
            ''')
            result = db.session.execute(user_query, {'user_id': last_id}).fetchone()
            user_dict = dict(result._mapping)
        
        # Tạo JWT tokens
        access_token = create_access_token(identity=user_dict['user_id'])
        refresh_token = create_refresh_token(identity=user_dict['user_id'])
        
        return jsonify({
            'success': True,
            'message': 'Đăng nhập Google thành công',
            'data': {
                'user': user_dict,
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"ERROR in google_callback: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Lỗi đăng nhập Google'
        }), 500

def validate_email(email):
    """Kiểm tra định dạng email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Kiểm tra độ mạnh mật khẩu"""
    if len(password) < 6:
        return "Mật khẩu phải có ít nhất 6 ký tự"
    return None

# ==================== AUTHENTICATION ====================

@user_bp.route('/auth/register', methods=['POST'])
def register():
    """Đăng ký tài khoản"""
    try:
        data = request.get_json()
        
        # Kiểm tra dữ liệu
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Vui lòng nhập {field}'
                }), 400
        
        # Validate email
        if not validate_email(data['email']):
            return jsonify({
                'success': False,
                'message': 'Email không hợp lệ'
            }), 400
        
        # Validate password
        password_error = validate_password(data['password'])
        if password_error:
            return jsonify({
                'success': False,
                'message': password_error
            }), 400
        
        # Validate username
        if len(data['username']) < 3 or len(data['username']) > 30:
            return jsonify({
                'success': False,
                'message': 'Username phải từ 3 đến 30 ký tự'
            }), 400
        
        # Đăng ký user
        user, error = UserService.register_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            full_name=data.get('full_name', ''),
            avatar_url=data.get('avatar_url', '')
        )
        
        if error:
            return jsonify({
                'success': False,
                'message': error
            }), 400
        
        # Tạo token
        access_token = create_access_token(identity=user['user_id'])
        refresh_token = create_refresh_token(identity=user['user_id'])
        
        return jsonify({
            'success': True,
            'message': 'Đăng ký thành công',
            'data': {
                'user': user,
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Lỗi server'
        }), 500

@user_bp.route('/auth/login', methods=['POST'])
def login():
    """Đăng nhập"""
    try:
        data = request.get_json()
        
        # Kiểm tra dữ liệu
        if not data.get('email') or not data.get('password'):
            return jsonify({
                'success': False,
                'message': 'Vui lòng nhập email và mật khẩu'
            }), 400
        
        # Xác thực user
        user, error = UserService.authenticate_user(data['email'], data['password'])
        
        if error:
            return jsonify({
                'success': False,
                'message': error
            }), 401
        
        # Tạo token
        access_token = create_access_token(identity=user['user_id'])
        refresh_token = create_refresh_token(identity=user['user_id'])
        
        return jsonify({
            'success': True,
            'message': 'Đăng nhập thành công',
            'data': {
                'user': user,
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Lỗi server'
        }), 500

@user_bp.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh token"""
    try:
        current_user_id = get_jwt_identity()
        access_token = create_access_token(identity=current_user_id)
        
        return jsonify({
            'success': True,
            'data': {
                'access_token': access_token
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Lỗi refresh token'
        }), 500

# ==================== USER PROFILE ====================

@user_bp.route('/users/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Lấy thông tin user hiện tại"""
    try:
        current_user_id = get_jwt_identity()
        user = UserService.get_user_by_id(current_user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User không tồn tại'
            }), 404
        
        return jsonify({
            'success': True,
            'data': user
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Lỗi server'
        }), 500

@user_bp.route('/users/me', methods=['PUT'])
@jwt_required()
def update_current_user():
    """Cập nhật thông tin user"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Không có dữ liệu'
            }), 400
        
        # Cập nhật user
        user, error = UserService.update_user(current_user_id, data)
        
        if error:
            return jsonify({
                'success': False,
                'message': error
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'Cập nhật thành công',
            'data': user
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Lỗi server'
        }), 500

@user_bp.route('/users/me/stats', methods=['GET'])
@jwt_required()
def get_my_stats():
    """Lấy thống kê cá nhân"""
    try:
        current_user_id = get_jwt_identity()
        stats, error = UserService.get_user_stats(current_user_id)
        
        if error:
            return jsonify({
                'success': False,
                'message': error
            }), 400
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Lỗi server'
        }), 500

# ==================== PUBLIC ENDPOINTS ====================

@user_bp.route('/users', methods=['GET'])
def get_users():
    """Lấy danh sách users (public)"""
    try:
        users = UserService.get_all_users()
        
        return jsonify({
            'success': True,
            'data': users,
            'count': len(users)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Lỗi server'
        }), 500

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Lấy thông tin user (public)"""
    try:
        user = UserService.get_user_by_id(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User không tồn tại'
            }), 404
        
        # Ẩn email cho public
        if 'email' in user:
            del user['email']
        
        return jsonify({
            'success': True,
            'data': user
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Lỗi server'
        }), 500

@user_bp.route('/users/leaderboard', methods=['GET'])
def get_leaderboard():
    """Lấy bảng xếp hạng"""
    try:
        limit = request.args.get('limit', 20, type=int)
        
        leaderboard, error = UserService.get_leaderboard(limit)
        
        if error:
            return jsonify({
                'success': False,
                'message': error
            }), 400
        
        return jsonify({
            'success': True,
            'data': leaderboard
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Lỗi server'
        }), 500

# ==================== SIMPLE AUTH CHECK ====================

@user_bp.route('/auth/check', methods=['GET'])
@jwt_required()
def check_auth():
    """Kiểm tra token còn hiệu lực không"""
    try:
        current_user_id = get_jwt_identity()
        user = UserService.get_user_by_id(current_user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User không tồn tại'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Token hợp lệ',
            'data': {
                'user_id': user['user_id'],
                'username': user['username']
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Token không hợp lệ'
        }), 401