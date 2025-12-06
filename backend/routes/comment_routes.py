# routes/comment_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.comment_service import CommentService
from extensions import db

comment_bp = Blueprint('comment', __name__)

@comment_bp.route('/comments', methods=['GET'])
def get_all_comments():
    """Lấy tất cả bình luận"""
    try:
        comments = CommentService.get_all_comments()
        return jsonify(comments)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@comment_bp.route('/comments/<int:comment_id>', methods=['GET'])
def get_comment(comment_id):
    """Lấy bình luận theo ID"""
    try:
        comment = CommentService.get_comment_by_id(comment_id)
        if not comment:
            return jsonify({'error': 'Comment not found'}), 404
        return jsonify(comment)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@comment_bp.route('/comments', methods=['POST'])
@jwt_required()
def create_comment():
    """Tạo bình luận mới"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Thêm user_id vào dữ liệu
        data['user_id'] = current_user_id
        
        comment, error = CommentService.create_comment(data)
        if error:
            return jsonify({'error': error}), 400
        return jsonify(comment), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@comment_bp.route('/comments/<int:comment_id>', methods=['PUT'])
@jwt_required()
def update_comment(comment_id):
    """Cập nhật bình luận"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Kiểm tra quyền sở hữu
        comment = CommentService.get_comment_by_id(comment_id)
        if not comment:
            return jsonify({'error': 'Comment not found'}), 404
        
        if comment['user_id'] != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        comment, error = CommentService.update_comment(comment_id, data)
        if error:
            return jsonify({'error': error}), 400
        return jsonify(comment)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@comment_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    """Xóa bình luận"""
    try:
        current_user_id = get_jwt_identity()
        
        # Kiểm tra quyền sở hữu
        comment = CommentService.get_comment_by_id(comment_id)
        if not comment:
            return jsonify({'error': 'Comment not found'}), 404
        
        if comment['user_id'] != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        success, error = CommentService.delete_comment(comment_id)
        if not success:
            return jsonify({'error': error}), 404
        return jsonify({'message': 'Comment deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@comment_bp.route('/comments/post/<int:post_id>', methods=['GET'])
def get_comments_by_post(post_id):
    """Lấy bình luận theo bài viết"""
    try:
        comments = CommentService.get_comments_by_post(post_id)
        return jsonify(comments)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@comment_bp.route('/comments/user/<int:user_id>', methods=['GET'])
def get_comments_by_user(user_id):
    """Lấy bình luận theo người dùng"""
    try:
        comments = CommentService.get_comments_by_user(user_id)
        return jsonify(comments)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@comment_bp.route('/comments/count/<int:post_id>', methods=['GET'])
def get_comment_count(post_id):
    """Lấy số bình luận của bài viết"""
    try:
        count = CommentService.get_comment_count_for_post(post_id)
        return jsonify({'post_id': post_id, 'comment_count': count})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@comment_bp.route('/comments/recent', methods=['GET'])
def get_recent_comments():
    """Lấy bình luận gần đây"""
    try:
        limit = request.args.get('limit', 10, type=int)
        comments = CommentService.get_recent_comments(limit=limit)
        return jsonify(comments)
    except Exception as e:
        return jsonify({'error': str(e)}), 500