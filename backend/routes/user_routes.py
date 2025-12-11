from flask import Blueprint, request, jsonify
from services.user_service import UserService
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from werkzeug.utils import secure_filename
from flask import current_app, send_from_directory
import os
from extensions import db

user_bp = Blueprint('user_bp', __name__)

# 1. Đăng ký
@user_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    result, error = UserService.register_user(data)
    
    if error:
        return jsonify({"status": "error", "message": error}), 400
    
    return jsonify({"status": "success", "data": result}), 201

# 2. Đăng nhập (Username/Pass)
@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    result, error = UserService.login_user(data)
    
    if error:
        return jsonify({"status": "error", "message": error}), 401
        
    return jsonify({"status": "success", "data": result}), 200

# 3. Đăng nhập Google
@user_bp.route('/google-login', methods=['POST'])
def google_login():
    try:
        data = request.get_json()
        print("DATA NHẬN ĐƯỢC:", data) # 1. Xem Frontend gửi gì lên

        token = data.get('credential')
        if not token:
            print("LỖI: Thiếu token")
            return jsonify({"status": "error", "message": "Thiếu token Google"}), 400

        result, error = UserService.google_login(token)
        
        if error:
            print("LỖI TỪ SERVICE:", error) # 2. Xem Service báo lỗi gì (quan trọng nhất)
            return jsonify({"status": "error", "message": error}), 400
            
        return jsonify({"status": "success", "data": result}), 200
    except Exception as e:
        print("LỖI EXCEPTION:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 400
    
# 4. Lấy thông tin User hiện tại (cần Token)
@user_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"status": "error", "message": "User không tồn tại"}), 404
        
    return jsonify({"status": "success", "data": user.to_dict()}), 200

# Hàm kiểm tra đuôi file hợp lệ (chỉ cho up ảnh)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@user_bp.route('/upload-avatar', methods=['POST'])
@jwt_required()
def upload_avatar():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "Không có file nào được gửi"}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"status": "error", "message": "Chưa chọn file"}), 400
        
    if file and allowed_file(file.filename):
        # 1. Lấy user hiện tại
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
             return jsonify({"status": "error", "message": "User không tồn tại"}), 404

        # 2. Xử lý tên file an toàn
        filename = secure_filename(file.filename)
        # Đặt tên file theo User ID để tránh trùng (user_123.jpg)
        file_ext = filename.rsplit('.', 1)[1].lower()
        new_filename = f"user_{current_user_id}.{file_ext}"
        
        # 3. Lưu file vào thư mục static/uploads/avatars
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER_AVATARS'], new_filename)
        
        # Tạo thư mục nếu chưa có
        if not os.path.exists(current_app.config['UPLOAD_FOLDER_AVATARS']):
            os.makedirs(current_app.config['UPLOAD_FOLDER_AVATARS'])
            
        file.save(save_path)
        
        # 4. Lưu đường dẫn vào Database
        # Lưu đường dẫn tương đối để Frontend gọi
        relative_path = f"/static/uploads/avatars/{new_filename}"
        
        user.avatar_url = relative_path
        db.session.commit()
        
        # Trả về đường dẫn đầy đủ (hoặc tương đối tùy bạn)
        # Ví dụ Frontend cần nối với: http://localhost:5000 + relative_path
        return jsonify({
            "status": "success", 
            "message": "Upload ảnh thành công", 
            "avatar_url": relative_path
        }), 200
        
    return jsonify({"status": "error", "message": "Định dạng file không hợp lệ (chỉ nhận jpg, png)"}), 400