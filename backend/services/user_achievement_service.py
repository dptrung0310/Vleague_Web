from extensions import db
from sqlalchemy import text
from datetime import datetime

class UserAchievementService:
    @staticmethod
    def get_all_user_achievements():
        try:
            query = text('''
                SELECT ua.*, u.username, a.name as achievement_name
                FROM UserAchievements ua
                LEFT JOIN Users u ON ua.user_id = u.user_id
                LEFT JOIN Achievements a ON ua.achievement_id = a.achievement_id
                ORDER BY ua.achieved_at DESC
            ''')
            result = db.session.execute(query)
            
            user_achievements = []
            for row in result:
                ua_dict = dict(row._mapping)
                
                if ua_dict.get('achieved_at'):
                    if isinstance(ua_dict['achieved_at'], str):
                        try:
                            ua_dict['achieved_at'] = datetime.strptime(
                                ua_dict['achieved_at'], '%Y-%m-%d %H:%M:%S'
                            ).isoformat()
                        except:
                            ua_dict['achieved_at'] = None
                    elif hasattr(ua_dict['achieved_at'], 'isoformat'):
                        ua_dict['achieved_at'] = ua_dict['achieved_at'].isoformat()
                
                user_achievements.append(ua_dict)
            
            return user_achievements
        except Exception as e:
            print(f"ERROR in get_all_user_achievements: {str(e)}")
            return []
    
    @staticmethod
    def get_user_achievement_by_id(user_achievement_id):
        try:
            query = text('''
                SELECT ua.*, u.username, a.name as achievement_name
                FROM UserAchievements ua
                LEFT JOIN Users u ON ua.user_id = u.user_id
                LEFT JOIN Achievements a ON ua.achievement_id = a.achievement_id
                WHERE ua.user_achievement_id = :id
            ''')
            result = db.session.execute(query, {'id': user_achievement_id}).fetchone()
            
            if result:
                ua_dict = dict(result._mapping)
                
                if ua_dict.get('achieved_at'):
                    if isinstance(ua_dict['achieved_at'], str):
                        try:
                            ua_dict['achieved_at'] = datetime.strptime(
                                ua_dict['achieved_at'], '%Y-%m-%d %H:%M:%S'
                            ).isoformat()
                        except:
                            ua_dict['achieved_at'] = None
                    elif hasattr(ua_dict['achieved_at'], 'isoformat'):
                        ua_dict['achieved_at'] = ua_dict['achieved_at'].isoformat()
                
                return ua_dict
            return None
        except Exception as e:
            print(f"ERROR in get_user_achievement_by_id: {str(e)}")
            return None
    
    @staticmethod
    def create_user_achievement(data):
        try:
            required_fields = ['user_id', 'achievement_id']
            for field in required_fields:
                if field not in data:
                    return None, f'{field} is required'
            
            # Kiểm tra xem user đã có achievement này chưa
            check_query = text('''
                SELECT COUNT(*) as count 
                FROM UserAchievements 
                WHERE user_id = :user_id AND achievement_id = :achievement_id
            ''')
            check_result = db.session.execute(check_query, {
                'user_id': data['user_id'],
                'achievement_id': data['achievement_id']
            }).fetchone()
            
            if check_result and check_result.count > 0:
                return None, "User already has this achievement"
            
            query = text('''
                INSERT INTO UserAchievements (user_id, achievement_id)
                VALUES (:user_id, :achievement_id)
            ''')
            
            db.session.execute(query, data)
            db.session.commit()
            
            # Lấy ID vừa tạo
            last_id = db.session.execute(text('SELECT last_insert_rowid()')).fetchone()[0]
            
            # Cộng điểm thưởng cho user (nếu có)
            achievement_query = text('SELECT points_reward FROM Achievements WHERE achievement_id = :achievement_id')
            achievement_result = db.session.execute(achievement_query, {
                'achievement_id': data['achievement_id']
            }).fetchone()
            
            if achievement_result and achievement_result.points_reward > 0:
                update_query = text('''
                    UPDATE Users 
                    SET points = points + :points 
                    WHERE user_id = :user_id
                ''')
                db.session.execute(update_query, {
                    'user_id': data['user_id'],
                    'points': achievement_result.points_reward
                })
                db.session.commit()
            
            return UserAchievementService.get_user_achievement_by_id(last_id), None
        except Exception as e:
            print(f"ERROR in create_user_achievement: {str(e)}")
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def delete_user_achievement(user_achievement_id):
        try:
            existing = UserAchievementService.get_user_achievement_by_id(user_achievement_id)
            if not existing:
                return False, "User achievement not found"
            
            query = text('DELETE FROM UserAchievements WHERE user_achievement_id = :id')
            db.session.execute(query, {'id': user_achievement_id})
            db.session.commit()
            
            return True, None
        except Exception as e:
            print(f"ERROR in delete_user_achievement: {str(e)}")
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def get_achievements_by_user(user_id):
        try:
            query = text('''
                SELECT a.*, ua.achieved_at,
                       CASE WHEN ua.user_achievement_id IS NOT NULL THEN 1 ELSE 0 END as is_unlocked
                FROM Achievements a
                LEFT JOIN UserAchievements ua ON a.achievement_id = ua.achievement_id AND ua.user_id = :user_id
                ORDER BY a.condition_value
            ''')
            result = db.session.execute(query, {'user_id': user_id})
            
            achievements = []
            for row in result:
                achievement_dict = dict(row._mapping)
                
                for field in ['created_at', 'achieved_at']:
                    if achievement_dict.get(field):
                        if isinstance(achievement_dict[field], str):
                            try:
                                achievement_dict[field] = datetime.strptime(
                                    achievement_dict[field], '%Y-%m-%d %H:%M:%S'
                                ).isoformat()
                            except:
                                achievement_dict[field] = None
                        elif hasattr(achievement_dict[field], 'isoformat'):
                            achievement_dict[field] = achievement_dict[field].isoformat()
                
                achievements.append(achievement_dict)
            
            return achievements
        except Exception as e:
            print(f"ERROR in get_achievements_by_user: {str(e)}")
            return []
    
    @staticmethod
    def get_recent_unlocks(limit=10):
        try:
            query = text('''
                SELECT ua.*, u.username, a.name as achievement_name, a.points_reward
                FROM UserAchievements ua
                LEFT JOIN Users u ON ua.user_id = u.user_id
                LEFT JOIN Achievements a ON ua.achievement_id = a.achievement_id
                ORDER BY ua.achieved_at DESC
                LIMIT :limit
            ''')
            result = db.session.execute(query, {'limit': limit})
            
            unlocks = []
            for row in result:
                unlock_dict = dict(row._mapping)
                
                if unlock_dict.get('achieved_at'):
                    if isinstance(unlock_dict['achieved_at'], str):
                        try:
                            unlock_dict['achieved_at'] = datetime.strptime(
                                unlock_dict['achieved_at'], '%Y-%m-%d %H:%M:%S'
                            ).isoformat()
                        except:
                            unlock_dict['achieved_at'] = None
                    elif hasattr(unlock_dict['achieved_at'], 'isoformat'):
                        unlock_dict['achieved_at'] = unlock_dict['achieved_at'].isoformat()
                
                unlocks.append(unlock_dict)
            
            return unlocks
        except Exception as e:
            print(f"ERROR in get_recent_unlocks: {str(e)}")
            return []