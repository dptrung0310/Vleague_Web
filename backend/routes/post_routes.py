# routes/post_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.post_service import PostService

post_bp = Blueprint('post_bp', __name__)

# 1. Tạo Post (dùng Form-Data vì có ảnh)
@post_bp.route('', methods=['POST'])
@jwt_required()
def create_post():
    user_id = get_jwt_identity()
    # request.form chứa text (title, content, match_id...)
    # request.files chứa file (image)
    result, error = PostService.create_post(user_id, request.form, request.files.get('image'))
    
    if error:
        return jsonify({"status": "error", "message": error}), 400
    return jsonify({"status": "success", "data": result}), 201

# 2. Lấy Newsfeed (Phân trang)
@post_bp.route('', methods=['GET'])
@jwt_required(optional=True) # Optional: để khách vãng lai cũng xem được
def get_posts():
    current_user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    
    # Lấy thêm tham số search
    search = request.args.get('search', '', type=str)

    result, error = PostService.get_all_posts(page, limit, current_user_id, search_query=search)
    
    if error:
        return jsonify({"status": "error", "message": error}), 400
    return jsonify({"status": "success", "data": result}), 200

# 3. Chi tiết bài viết
@post_bp.route('/<int:post_id>', methods=['GET'])
@jwt_required(optional=True)
def get_post_detail(post_id):
    current_user_id = get_jwt_identity()
    result, error = PostService.get_post_detail(post_id, current_user_id)
    
    if error:
        return jsonify({"status": "error", "message": error}), 404
    return jsonify({"status": "success", "data": result}), 200

# 4. Like / Unlike
@post_bp.route('/<int:post_id>/like', methods=['POST'])
@jwt_required()
def like_post(post_id):
    user_id = get_jwt_identity()
    action, error = PostService.toggle_like(user_id, post_id)
    
    if error:
        return jsonify({"status": "error", "message": error}), 400
    return jsonify({"status": "success", "message": action}), 200

# 5. Comment
@post_bp.route('/<int:post_id>/comment', methods=['POST'])
@jwt_required()
def comment_post(post_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    result, error = PostService.add_comment(user_id, post_id, data.get('content'))
    
    if error:
        return jsonify({"status": "error", "message": error}), 400
    return jsonify({"status": "success", "data": result}), 201

# 6. Xóa bài viết
@post_bp.route('/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    user_id = get_jwt_identity()
    
    msg, error = PostService.delete_post(user_id, post_id)
    
    if error:
        # Trả về 403 Forbidden nếu không có quyền, hoặc 404/400 tùy lỗi
        if "quyền" in error:
            return jsonify({"status": "error", "message": error}), 403
        return jsonify({"status": "error", "message": error}), 400
        
    return jsonify({"status": "success", "message": msg}), 200