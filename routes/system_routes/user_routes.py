from flask import request
from flask_restx import Resource
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from extensions import cache
from services.system_services.user_service import UserService


def init_user_routes(api, namespace, schemas):
    user_service = UserService()

    # Models
    register_model = schemas['user_register']
    update_model = schemas['user_update']
    user_output = schemas['user_output']
    login_input = schemas['login_input']
    auth_response = schemas['auth_response']

    @namespace.route('/register')
    class UserRegister(Resource):
        @namespace.doc('register_user')
        @namespace.expect(register_model, validate=True)
        def post(self):
            """Đăng ký tài khoản mới"""
            return user_service.create_user(request.json)

    @namespace.route('/login')
    class UserLogin(Resource):
        @namespace.doc('login_user')
        @namespace.expect(login_input, validate=True)
        @namespace.response(200, 'Success', auth_response)
        def post(self):
            """Đăng nhập và lấy JWT Token"""
            data = request.json
            result, status_code = user_service.login(data['username'], data['password'])

            if status_code == 200:
                user = result['user']
                # Tạo JWT Token
                # identity là user_id (int) hoặc chuỗi tùy quy ước
                access_token = create_access_token(identity=user['user_id'], additional_claims={'role': user['role']})
                refresh_token = create_refresh_token(identity=user['user_id'])

                return {
                    'message': 'Đăng nhập thành công',
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'user': user
                }, 200

            return result, status_code

    @namespace.route('/profile')
    class UserProfile(Resource):
        @namespace.doc('get_my_profile', security='jwt')
        @namespace.marshal_with(user_output)
        @jwt_required()
        def get(self):
            """Lấy thông tin của chính mình (dựa trên Token)"""
            current_user_id = get_jwt_identity()
            return user_service.get_user_by_id(current_user_id)

    @namespace.route('')
    class UserList(Resource):
        @namespace.doc('list_users', security='jwt')
        @namespace.marshal_list_with(user_output)
        @jwt_required()  # Thường chỉ Admin mới được xem list user
        def get(self):
            """Lấy danh sách tất cả người dùng (Admin)"""
            return user_service.get_all_users()

    @namespace.route('/<int:id>')
    @namespace.param('id', 'User ID')
    class UserResource(Resource):
        @namespace.doc('get_user', security='jwt')
        @namespace.marshal_with(user_output)
        @jwt_required()
        def get(self, id):
            """Xem thông tin user khác"""
            return user_service.get_user_by_id(id)

        @namespace.doc('update_user', security='jwt')
        @namespace.expect(update_model)
        @jwt_required()
        def put(self, id):
            """Cập nhật thông tin user"""
            # Cần check quyền: chỉ update chính mình hoặc là admin
            return user_service.update_user(id, request.json)

        @namespace.doc('delete_user', security='jwt')
        @jwt_required()
        def delete(self, id):
            """Xóa user (Admin)"""
            return user_service.delete_user(id)