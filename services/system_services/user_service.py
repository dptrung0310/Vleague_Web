import bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token
from sqlalchemy import or_

from models.system_models.user import User
from services.base import BaseService


class UserService(BaseService):

    # --- HELPER METHODS (Hàm phụ trợ) ---
    def _hash_password(self, password):
        """Băm mật khẩu bằng Bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def _generate_tokens(self, user):
        """Tạo JWT Token trả về cho client"""
        user_identity = str(user.user_id)

        access_token = create_access_token(
            identity=user_identity,
            additional_claims={'role': user.role}
        )
        refresh_token = create_refresh_token(identity=user_identity)

        return {
            'message': 'Thành công',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }, 200

    # --- AUTHENTICATION METHODS (Đăng nhập/Đăng ký) ---

    def create_user_form(self, data):
        """Đăng ký tài khoản mới qua Form"""
        # 1. Validate cơ bản
        if 'password' not in data or not data['password']:
            return {'message': 'Mật khẩu là bắt buộc.'}, 400

        # 2. Check trùng username/email
        existing = User.query.filter(or_(User.username == data['username'], User.email == data['email'])).first()
        if existing:
            return {'message': 'Username hoặc Email đã tồn tại.'}, 409

        # 3. Tạo user và lưu bằng BaseService
        new_user = User(
            username=data['username'],
            email=data['email'],
            password_hash=self._hash_password(data['password']),
            role='user'
        )

        # BaseService tự lo commit/rollback
        success, result = self.save(new_user)
        if success:
            return {'message': 'Đăng ký thành công', 'user': result.to_dict()}, 201
        return {'message': f'Lỗi hệ thống: {result}'}, 500

    def login_form(self, username_or_email, password):
        """Đăng nhập bằng Username/Password"""
        user = User.query.filter(or_(User.username == username_or_email, User.email == username_or_email)).first()

        if not user:
            return {'message': 'Tài khoản không tồn tại.'}, 401

        # Nếu user này tạo từ Google (không có pass) -> Báo lỗi
        if user.password_hash is None:
            return {'message': 'Email này dùng đăng nhập Google. Vui lòng chọn Google Login.'}, 400

        # Kiểm tra mật khẩu
        if bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return self._generate_tokens(user)

        return {'message': 'Mật khẩu không đúng.'}, 401

    def login_with_google(self, user_info):
        """Xử lý đăng nhập/đăng ký qua Google"""
        email = user_info.get('email')
        google_id = user_info.get('sub')

        user = User.query.filter_by(email=email).first()

        if user:
            # Case 1: Đã có user -> Cập nhật google_id nếu thiếu (Link Account)
            if not user.google_id:
                user.google_id = google_id
                self.save(user)  # Update nhẹ nhàng
        else:
            # Case 2: User mới -> Tạo user không pass
            # Tự sinh username từ email (ví dụ: nam@gmail.com -> nam)
            # Cần xử lý nếu username bị trùng (thêm số ngẫu nhiên nếu cần, ở đây làm đơn giản trước)
            base_username = email.split('@')[0]

            user = User(
                username=base_username,
                email=email,
                role='user',
                google_id=google_id,
                password_hash=None  # Quan trọng: Không có pass
            )
            success, result = self.save(user)
            if not success:
                return {'message': 'Lỗi tạo user Google', 'error': result}, 500
            user = result

        return self._generate_tokens(user)

    # --- CRUD STANDARD METHODS (Tận dụng BaseService) ---

    def get_all_users(self):
        return [u.to_dict() for u in User.query.all()], 200

    def get_user_by_id(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {'message': 'Không tìm thấy người dùng.'}, 404
        return user.to_dict(), 200

    def update_user(self, user_id, data):
        user = User.query.get(user_id)
        if not user:
            return {'message': 'Không tìm thấy người dùng.'}, 404

        # Logic update
        if 'email' in data and data['email'] != user.email:
            if User.query.filter_by(email=data['email']).first():
                return {'message': 'Email đã tồn tại.'}, 409
            user.email = data['email']

        if 'role' in data:
            user.role = data['role']

        # Nếu đổi pass mới
        if 'password' in data and data['password']:
            user.password_hash = self._hash_password(data['password'])

        success, result = self.save(user)
        if success:
            return {'message': 'Cập nhật thành công', 'user': result.to_dict()}, 200
        return {'message': f'Lỗi cập nhật: {result}'}, 500

    def delete_user(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {'message': 'Không tìm thấy người dùng.'}, 404

        success, result = self.delete(user)
        if success:
            return {'message': 'Xóa thành công.'}, 200
        return {'message': f'Lỗi xóa: {result}'}, 500