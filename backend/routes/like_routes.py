# routes/like_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.like_service import LikeService
from extensions import db

like_bp = Blueprint('like', __name__)

@like_bp.route('/likes', methods=['GET'])
def get_all_likes():
    """Lấy tất cả lượt like"""
    try:
        likes = LikeService.get_all_likes()
        return jsonify(likes)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@like_bp.route('/likes/<int:like_id>', methods=['GET'])
def get_like(like_id):
    """Lấy lượt like theo ID"""
    try:
        like = LikeService.get_like_by_id(like_id)
        if not like:
            return jsonify({'error': 'Like not found'}), 404
        return jsonify(like)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@like_bp.route('/likes', methods=['POST'])
@jwt_required()
def create_like():
    """Tạo lượt like mới"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Thêm user_id vào dữ liệu
        data['user_id'] = current_user_id
        
        like, error = LikeService.create_like(data)
        if error:
            return jsonify({'error': error}), 400
        return jsonify(like), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@like_bp.route('/likes/<int:like_id>', methods=['DELETE'])
@jwt_required()
def delete_like(like_id):
    """Xóa lượt like"""
    try:
        current_user_id = get_jwt_identity()
        
        # Kiểm tra quyền sở hữu
        like = LikeService.get_like_by_id(like_id)
        if not like:
            return jsonify({'error': 'Like not found'}), 404
        
        if like['user_id'] != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        success, error = LikeService.delete_like(like_id)
        if not success:
            return jsonify({'error': error}), 404
        return jsonify({'message': 'Like deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@like_bp.route('/likes/unlike', methods=['DELETE'])
@jwt_required()
def unlike_post():
    """Bỏ like bài viết"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'post_id' not in data:
            return jsonify({'error': 'post_id is required'}), 400
        
        success, error = LikeService.unlike_post(current_user_id, data['post_id'])
        if not success:
            return jsonify({'error': error or 'Like not found'}), 404
        return jsonify({'message': 'Post unliked successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@like_bp.route('/likes/post/<int:post_id>', methods=['GET'])
def get_likes_by_post(post_id):
    """Lấy lượt like theo bài viết"""
    try:
        likes = LikeService.get_likes_by_post(post_id)
        return jsonify(likes)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@like_bp.route('/likes/user/<int:user_id>', methods=['GET'])
def get_likes_by_user(user_id):
    """Lấy lượt like theo người dùng"""
    try:
        likes = LikeService.get_likes_by_user(user_id)
        return jsonify(likes)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@like_bp.route('/likes/check', methods=['GET'])
@jwt_required()
def check_like():
    """Kiểm tra người dùng đã like bài viết chưa"""
    try:
        current_user_id = get_jwt_identity()
        post_id = request.args.get('post_id', type=int)
        
        if not post_id:
            return jsonify({'error': 'post_id is required'}), 400
        
        is_liked = LikeService.is_post_liked_by_user(current_user_id, post_id)
        return jsonify({'is_liked': is_liked})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@like_bp.route('/likes/count/<int:post_id>', methods=['GET'])
def get_like_count(post_id):
    """Lấy số lượt like của bài viết"""
    try:
        count = LikeService.get_like_count_for_post(post_id)
        return jsonify({'post_id': post_id, 'like_count': count})
    except Exception as e:
        return jsonify({'error': str(e)}), 500