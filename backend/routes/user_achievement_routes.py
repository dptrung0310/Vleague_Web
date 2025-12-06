# routes/user_achievement_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.user_achievement_service import UserAchievementService
from extensions import db

user_achievement_bp = Blueprint('user_achievement', __name__)

@user_achievement_bp.route('/user-achievements', methods=['GET'])
@jwt_required()
def get_all_user_achievements():
    """Lấy tất cả thành tựu người dùng"""
    try:
        user_achievements = UserAchievementService.get_all_user_achievements()
        return jsonify(user_achievements)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_achievement_bp.route('/user-achievements/<int:user_achievement_id>', methods=['GET'])
def get_user_achievement(user_achievement_id):
    """Lấy thành tựu người dùng theo ID"""
    try:
        user_achievement = UserAchievementService.get_user_achievement_by_id(user_achievement_id)
        if not user_achievement:
            return jsonify({'error': 'User achievement not found'}), 404
        return jsonify(user_achievement)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_achievement_bp.route('/user-achievements', methods=['POST'])
@jwt_required()
def create_user_achievement():
    """Gán thành tựu cho người dùng"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Thêm user_id vào dữ liệu
        data['user_id'] = current_user_id
        
        user_achievement, error = UserAchievementService.create_user_achievement(data)
        if error:
            return jsonify({'error': error}), 400
        return jsonify(user_achievement), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_achievement_bp.route('/user-achievements/<int:user_achievement_id>', methods=['DELETE'])
@jwt_required()
def delete_user_achievement(user_achievement_id):
    """Xóa thành tựu người dùng"""
    try:
        current_user_id = get_jwt_identity()
        
        # Kiểm tra quyền sở hữu
        user_achievement = UserAchievementService.get_user_achievement_by_id(user_achievement_id)
        if not user_achievement:
            return jsonify({'error': 'User achievement not found'}), 404
        
        if user_achievement['user_id'] != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        success, error = UserAchievementService.delete_user_achievement(user_achievement_id)
        if not success:
            return jsonify({'error': error}), 404
        return jsonify({'message': 'User achievement deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_achievement_bp.route('/user-achievements/user/<int:user_id>', methods=['GET'])
def get_achievements_by_user(user_id):
    """Lấy thành tựu theo người dùng"""
    try:
        achievements = UserAchievementService.get_achievements_by_user(user_id)
        return jsonify(achievements)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_achievement_bp.route('/user-achievements/recent', methods=['GET'])
def get_recent_unlocks():
    """Lấy thành tựu được mở khóa gần đây"""
    try:
        limit = request.args.get('limit', 10, type=int)
        unlocks = UserAchievementService.get_recent_unlocks(limit=limit)
        return jsonify(unlocks)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_achievement_bp.route('/user-achievements/my-achievements', methods=['GET'])
@jwt_required()
def get_my_achievements():
    """Lấy thành tựu của người dùng hiện tại"""
    try:
        current_user_id = get_jwt_identity()
        achievements = UserAchievementService.get_achievements_by_user(current_user_id)
        return jsonify(achievements)
    except Exception as e:
        return jsonify({'error': str(e)}), 500