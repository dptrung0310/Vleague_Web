from models.user import User
from extensions import db
from flask_jwt_extended import create_access_token
from google.oauth2 import id_token
from google.auth.transport import requests
import os

class UserService:
    
    # --- ĐĂNG KÝ ---
    @staticmethod
    def register_user(data):
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name')

        if not username or not email or not password:
            return None, "Vui lòng nhập đầy đủ thông tin"
        if User.query.filter_by(username=username).first():
            return None, "Tên đăng nhập đã tồn tại"
        if User.query.filter_by(email=email).first():
            return None, "Email đã được sử dụng"
        
        new_user = User(
            username=username,
            email=email,
            full_name=full_name
        )
        new_user.set_password(password) # Hàm này đã có trong user.py
        
        try:
            db.session.add(new_user)
            db.session.commit()
            
            # Tạo token ngay sau khi đăng ký thành công (để user tự login luôn)
            access_token = create_access_token(identity=str(new_user.user_id))
            
            return {
                "message": "Đăng ký thành công",
                "access_token": access_token,
                "user": new_user.to_dict()
            }, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    # --- ĐĂNG NHẬP (Thường) ---
    @staticmethod
    def login_user(data):
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()
        
        # Nếu không tìm thấy bằng username, thử tìm bằng email
        if not user:
            user = User.query.filter_by(email=username).first()

        if user and user.check_password(password):
            access_token = create_access_token(identity=str(user.user_id))
            return {
                "message": "Đăng nhập thành công",
                "access_token": access_token,
                "user": user.to_dict()
            }, None
        
        return None, "Sai tên đăng nhập hoặc mật khẩu"

    # --- ĐĂNG NHẬP GOOGLE ---
    @staticmethod
    def google_login(google_token):
        try:
            # 1. Xác thực token gửi lên từ Frontend với Google
            client_id = os.environ.get('GOOGLE_CLIENT_ID')
            id_info = id_token.verify_oauth2_token(google_token, requests.Request(), client_id)

            # 2. Lấy thông tin từ Google
            email = id_info.get('email')
            name = id_info.get('name')
            google_id = id_info.get('sub')
            picture = id_info.get('picture')

            # 3. Kiểm tra xem email này đã có trong DB chưa
            user = User.query.filter_by(email=email).first()

            if not user:
                # Nếu chưa có -> Tự động Đăng ký
                # Tạo username từ email (bỏ phần @gmail.com) + random số nếu cần
                base_username = email.split('@')[0]
                username = base_username
                
                # Xử lý trùng username khi tạo tự động
                counter = 1
                while User.query.filter_by(username=username).first():
                    username = f"{base_username}{counter}"
                    counter += 1

                user = User(
                    username=username,
                    email=email,
                    full_name=name,
                    google_id=google_id,
                    avatar_url=picture
                )
                # Google user không cần password, nhưng set random string để an toàn
                import secrets
                user.set_password(secrets.token_hex(16))
                
                db.session.add(user)
                db.session.commit()
            else:
                # Nếu đã có, cập nhật google_id/avatar nếu chưa có
                if not user.google_id:
                    user.google_id = google_id
                if not user.avatar_url:
                    user.avatar_url = picture
                db.session.commit()

            # 4. Tạo JWT Token
            access_token = create_access_token(identity=str(user.user_id))
            return {
                "message": "Google login thành công",
                "access_token": access_token,
                "user": user.to_dict()
            }, None

        except ValueError:
            return None, "Token Google không hợp lệ"
        except Exception as e:
            return None, str(e)