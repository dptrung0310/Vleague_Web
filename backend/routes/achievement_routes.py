from flask import Blueprint, request, jsonify
from services.achievement_service import AchievementService

achievement_bp = Blueprint('achievements', __name__)

@achievement_bp.route('/achievements', methods=['GET'])
def get_achievements():
    user_id = request.args.get('user_id', type=int)
    
    if user_id:
        achievements = AchievementService.get_user_achievements(user_id)
    else:
        achievements = AchievementService.get_all_achievements()
    
    return jsonify(achievements)

@achievement_bp.route('/achievements/<int:achievement_id>', methods=['GET'])
def get_achievement(achievement_id):
    achievement = AchievementService.get_achievement_by_id(achievement_id)
    if not achievement:
        return jsonify({'error': 'Achievement not found'}), 404
    return jsonify(achievement)

@achievement_bp.route('/achievements', methods=['POST'])
def create_achievement():
    data = request.json
    
    achievement, error = AchievementService.create_achievement(data)
    if error:
        return jsonify({'error': error}), 400
    
    if achievement:
        return jsonify(achievement), 201
    return jsonify({'error': 'Failed to create achievement'}), 500

@achievement_bp.route('/achievements/<int:achievement_id>', methods=['PUT'])
def update_achievement(achievement_id):
    data = request.json
    
    achievement, error = AchievementService.update_achievement(achievement_id, data)
    if error:
        return jsonify({'error': error}), 400
    
    if not achievement:
        return jsonify({'error': 'Achievement not found'}), 404
    
    return jsonify(achievement)

@achievement_bp.route('/achievements/<int:achievement_id>', methods=['DELETE'])
def delete_achievement(achievement_id):
    success, error = AchievementService.delete_achievement(achievement_id)
    if error:
        return jsonify({'error': error}), 400
    
    if not success:
        return jsonify({'error': 'Achievement not found'}), 404
    
    return jsonify({'message': 'Achievement deleted successfully'}), 200

@achievement_bp.route('/achievements/check/<int:user_id>', methods=['POST'])
def check_achievements(user_id):
    unlocked = AchievementService.check_and_unlock_achievements(user_id)
    return jsonify(unlocked)