# routes/post_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.post_service import PostService
from extensions import db
from models import Post, User

post_bp = Blueprint('post', __name__)

# routes/post_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.post_service import PostService

post_bp = Blueprint('post', __name__)

@post_bp.route('/posts', methods=['GET'])
def get_all_posts():
    """Lấy tất cả bài viết"""
    try:
        include_counts = request.args.get('include_counts', 'false').lower() == 'true'
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Có thể thêm pagination vào service
        posts = PostService.get_all_posts(include_counts=include_counts)
        
        if limit:
            posts = posts[offset:offset + limit]
        
        return jsonify({
            'success': True,
            'data': posts,
            'count': len(posts),
            'limit': limit,
            'offset': offset
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@post_bp.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """Lấy bài viết theo ID"""
    try:
        include_counts = request.args.get('include_counts', 'false').lower() == 'true'
        post = PostService.get_post_by_id(post_id, include_counts=include_counts)
        
        if not post:
            return jsonify({'success': False, 'error': 'Post not found'}), 404
        
        return jsonify({'success': True, 'data': post})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@post_bp.route('/posts', methods=['POST'])
@jwt_required()
def create_post():
    """Tạo bài viết mới"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Thêm user_id từ JWT
        data['user_id'] = current_user_id
        
        post, error = PostService.create_post(data)
        
        if error:
            return jsonify({'success': False, 'error': error}), 400
        
        return jsonify({'success': True, 'data': post}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@post_bp.route('/posts/<int:post_id>', methods=['PUT'])
@jwt_required()
def update_post(post_id):
    """Cập nhật bài viết"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Kiểm tra quyền sở hữu
        post = PostService.get_post_by_id(post_id)
        if not post:
            return jsonify({'error': 'Post not found'}), 404
        
        if post['user_id'] != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        post, error = PostService.update_post(post_id, data)
        if error:
            return jsonify({'error': error}), 400
        return jsonify(post)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@post_bp.route('/posts/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    """Xóa bài viết"""
    try:
        current_user_id = get_jwt_identity()
        
        # Kiểm tra quyền sở hữu
        post = PostService.get_post_by_id(post_id)
        if not post:
            return jsonify({'error': 'Post not found'}), 404
        
        if post['user_id'] != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        success, error = PostService.delete_post(post_id)
        if not success:
            return jsonify({'error': error}), 404
        return jsonify({'message': 'Post deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@post_bp.route('/posts/user/<int:user_id>', methods=['GET'])
def get_posts_by_user(user_id):
    """Lấy bài viết theo người dùng"""
    try:
        include_counts = request.args.get('include_counts', 'false').lower() == 'true'
        posts = PostService.get_posts_by_user(user_id, include_counts=include_counts)
        return jsonify(posts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@post_bp.route('/posts/match/<int:match_id>', methods=['GET'])
def get_posts_by_match(match_id):
    """Lấy bài viết theo trận đấu"""
    try:
        posts = PostService.get_posts_by_match(match_id)
        return jsonify(posts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@post_bp.route('/posts/search', methods=['GET'])
def search_posts():
    """Tìm kiếm bài viết"""
    try:
        keyword = request.args.get('keyword', '')
        if not keyword:
            return jsonify({'error': 'Keyword is required'}), 400
        
        posts = PostService.search_posts(keyword)
        return jsonify(posts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@post_bp.route('/posts/trending', methods=['GET'])
def get_trending_posts():
    """Lấy bài viết trending"""
    try:
        limit = request.args.get('limit', 10, type=int)
        posts = PostService.get_trending_posts(limit=limit)
        return jsonify(posts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500