import bcrypt
from models.system_models.user import User
from services.base import BaseService
from sqlalchemy import or_


class UserService(BaseService):
    def get_all_users(self):
        users = User.query.all()
        return [u.to_dict() for u in users], 200

    def get_user_by_id(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {'message': 'Không tìm thấy người dùng.'}, 404
        return user.to_dict(), 200

    def _hash_password(self, password):
        """Hàm phụ trợ để băm mật khẩu"""
        # bcrypt yêu cầu input là bytes, nên cần .encode('utf-8')
        # hashpw trả về bytes, cần .decode('utf-8') để lưu vào DB cột String
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return hashed.decode('utf-8')

    def create_user(self, data):
        # 1. Kiểm tra trùng username hoặc email
        existing_user = User.query.filter(
            or_(User.username == data['username'], User.email == data['email'])
        ).first()

        if existing_user:
            return {'message': 'Username hoặc Email đã tồn tại.'}, 409

        # 2. Kiểm tra có password không
        if 'password' not in data:
            return {'message': 'Mật khẩu là bắt buộc.'}, 400

        # 3. Hash mật khẩu
        hashed_pw = self._hash_password(data['password'])

        new_user = User(
            username=data['username'],
            email=data['email'],
            password_hash=hashed_pw,  # Lưu mật khẩu đã băm
            role=data.get('role', 'user')
        )

        success, result = self.save(new_user)
        if success:
            return {'message': 'Đăng ký thành công', 'user': result.to_dict()}, 201
        return {'message': f'Lỗi DB: {result}'}, 500

    def update_user(self, user_id, data):
        user = User.query.get(user_id)
        if not user:
            return {'message': 'Không tìm thấy người dùng.'}, 404

        if 'email' in data and data['email'] != user.email:
            if User.query.filter_by(email=data['email']).first():
                return {'message': 'Email đã được sử dụng.'}, 409
            user.email = data['email']

        user.role = data.get('role', user.role)

        # Nếu người dùng muốn đổi mật khẩu mới
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
            return {'message': 'Xóa người dùng thành công.'}, 200
        return {'message': f'Lỗi xóa: {result}'}, 500

    # --- Hàm mới dùng để Login ---
    def login(self, username_or_email, password):
        """Xác thực người dùng khi đăng nhập"""
        # Tìm user theo username hoặc email
        user = User.query.filter(
            or_(User.username == username_or_email, User.email == username_or_email)
        ).first()

        if not user:
            return {'message': 'Tài khoản hoặc mật khẩu không đúng.'}, 401

        # Kiểm tra mật khẩu bằng bcrypt
        # user.password_hash trong DB là chuỗi, cần encode lại thành bytes để so sánh
        if bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return {'message': 'Đăng nhập thành công', 'user': user.to_dict()}, 200
        else:
            return {'message': 'Tài khoản hoặc mật khẩu không đúng.'}, 401