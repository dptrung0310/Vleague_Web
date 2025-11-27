from flask import request, redirect, url_for
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from flask_restx import Resource
from extensions import oauth
from services.system_services.user_service import UserService


def init_user_routes(api, namespace, schemas):
    user_service = UserService()

    # Models
    register_model = schemas['user_register']
    update_model = schemas['user_update']
    user_output = schemas['user_output']
    login_input = schemas['login_input']
    auth_response = schemas['auth_response']

    @namespace.route('')
    class UserRegister(Resource):
        @namespace.doc('register_user')
        @namespace.expect(register_model, validate=True)
        def post(self):
            """Đăng ký tài khoản mới"""
            return user_service.create_user_form(request.json)

    @namespace.route('/login')
    class UserLogin(Resource):
        @namespace.doc('login_user')
        @namespace.expect(login_input, validate=True)
        @namespace.response(200, 'Success', auth_response)
        def post(self):
            """Đăng nhập và lấy JWT Token"""
            data = request.json

            # Service đã trả về {message, access_token, refresh_token, user} rồi
            result, status_code = user_service.login_form(data['username'], data['password'])

            # Chỉ cần trả về kết quả từ service là xong
            return result, status_code

    @namespace.route('/google')
    class GoogleLogin(Resource):
        def get(self):
            """Redirect user sang trang Google"""
            # Redirect URI phải trùng khớp setting trong Google Cloud Console
            redirect_uri = url_for('Users_google_callback', _external=True)
            return oauth.google.authorize_redirect(redirect_uri)

    @namespace.route('/google/callback')
    class GoogleCallback(Resource):
        def get(self):
            """Google gọi về đây kèm code"""
            try:
                token = oauth.google.authorize_access_token()
                user_info = token.get('userinfo')

                # Gọi service xử lý (Login hoặc Register ngầm)
                result, _ = user_service.login_with_google(user_info)

                # VÌ ĐÂY LÀ BROWSER REDIRECT, TA KHÔNG TRẢ JSON ĐƯỢC
                # Phải redirect về Frontend kèm Token trên URL
                frontend_url = "http://localhost:5173/auth/callback"
                access_token = result['access_token']
                refresh_token = result['refresh_token']

                return redirect(f"{frontend_url}?access_token={access_token}&refresh_token={refresh_token}")

            except Exception as e:
                return {"message": "Lỗi xác thực Google", "error": str(e)}, 400

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