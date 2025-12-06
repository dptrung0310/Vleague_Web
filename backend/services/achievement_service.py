from extensions import db
from sqlalchemy import text
from datetime import datetime

class AchievementService:
    @staticmethod
    def get_all_achievements():
        try:
            query = text('SELECT * FROM Achievements ORDER BY condition_value')
            result = db.session.execute(query)
            
            achievements = []
            for row in result:
                achievement_dict = dict(row._mapping)
                # Xử lý datetime
                if achievement_dict.get('created_at'):
                    if isinstance(achievement_dict['created_at'], str):
                        try:
                            achievement_dict['created_at'] = datetime.strptime(
                                achievement_dict['created_at'], '%Y-%m-%d %H:%M:%S'
                            ).isoformat()
                        except:
                            achievement_dict['created_at'] = None
                    elif hasattr(achievement_dict['created_at'], 'isoformat'):
                        achievement_dict['created_at'] = achievement_dict['created_at'].isoformat()
                
                achievements.append(achievement_dict)
            
            return achievements
        except Exception as e:
            print(f"ERROR in get_all_achievements: {str(e)}")
            return []
    
    @staticmethod
    def get_achievement_by_id(achievement_id):
        try:
            query = text('SELECT * FROM Achievements WHERE achievement_id = :id')
            result = db.session.execute(query, {'id': achievement_id}).fetchone()
            
            if result:
                achievement_dict = dict(result._mapping)
                if achievement_dict.get('created_at'):
                    if isinstance(achievement_dict['created_at'], str):
                        try:
                            achievement_dict['created_at'] = datetime.strptime(
                                achievement_dict['created_at'], '%Y-%m-%d %H:%M:%S'
                            ).isoformat()
                        except:
                            achievement_dict['created_at'] = None
                    elif hasattr(achievement_dict['created_at'], 'isoformat'):
                        achievement_dict['created_at'] = achievement_dict['created_at'].isoformat()
                
                return achievement_dict
            return None
        except Exception as e:
            print(f"ERROR in get_achievement_by_id: {str(e)}")
            return None
    
    @staticmethod
    def create_achievement(data):
        try:
            columns = []
            values = []
            params = {}
            
            required_fields = ['name', 'condition_type', 'condition_value']
            for field in required_fields:
                if field not in data:
                    return None, f'{field} is required'
            
            for key, value in data.items():
                columns.append(key)
                values.append(f":{key}")
                params[key] = value
            
            query = text(f'''
                INSERT INTO Achievements ({', '.join(columns)})
                VALUES ({', '.join(values)})
            ''')
            
            db.session.execute(query, params)
            db.session.commit()
            
            # Lấy ID vừa tạo
            last_id = db.session.execute(text('SELECT last_insert_rowid()')).fetchone()[0]
            
            return AchievementService.get_achievement_by_id(last_id), None
        except Exception as e:
            print(f"ERROR in create_achievement: {str(e)}")
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def update_achievement(achievement_id, data):
        try:
            existing = AchievementService.get_achievement_by_id(achievement_id)
            if not existing:
                return None, "Achievement not found"
            
            set_clause = ', '.join([f"{key} = :{key}" for key in data.keys()])
            query = text(f'''
                UPDATE Achievements 
                SET {set_clause}
                WHERE achievement_id = :achievement_id
            ''')
            
            params = data.copy()
            params['achievement_id'] = achievement_id
            
            db.session.execute(query, params)
            db.session.commit()
            
            return AchievementService.get_achievement_by_id(achievement_id), None
        except Exception as e:
            print(f"ERROR in update_achievement: {str(e)}")
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def delete_achievement(achievement_id):
        try:
            existing = AchievementService.get_achievement_by_id(achievement_id)
            if not existing:
                return False, "Achievement not found"
            
            query = text('DELETE FROM Achievements WHERE achievement_id = :achievement_id')
            db.session.execute(query, {'achievement_id': achievement_id})
            db.session.commit()
            
            return True, None
        except Exception as e:
            print(f"ERROR in delete_achievement: {str(e)}")
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def get_user_achievements(user_id):
        try:
            query = text('''
                SELECT a.*, ua.achieved_at
                FROM UserAchievements ua
                LEFT JOIN Achievements a ON ua.achievement_id = a.achievement_id
                WHERE ua.user_id = :user_id
                ORDER BY ua.achieved_at DESC
            ''')
            result = db.session.execute(query, {'user_id': user_id})
            
            achievements = []
            for row in result:
                achievement_dict = dict(row._mapping)
                
                # Xử lý datetime
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
            print(f"ERROR in get_user_achievements: {str(e)}")
            return []
    
    @staticmethod
    def get_unlocked_achievements(user_id):
        try:
            query = text('''
                SELECT a.*, ua.achieved_at
                FROM UserAchievements ua
                LEFT JOIN Achievements a ON ua.achievement_id = a.achievement_id
                WHERE ua.user_id = :user_id
                ORDER BY ua.achieved_at DESC
            ''')
            result = db.session.execute(query, {'user_id': user_id})
            
            unlocked = [dict(row._mapping) for row in result]
            return unlocked
        except Exception as e:
            print(f"ERROR in get_unlocked_achievements: {str(e)}")
            return []
    
    @staticmethod
    def check_and_unlock_achievements(user_id):
        """Kiểm tra và mở khóa thành tích dựa trên hoạt động của user"""
        try:
            # Lấy thông tin user
            user_query = text('''
                SELECT points, correct_predictions, total_predictions 
                FROM Users WHERE user_id = :user_id
            ''')
            user_result = db.session.execute(user_query, {'user_id': user_id}).fetchone()
            
            if not user_result:
                return []
            
            points, correct_predictions, total_predictions = user_result
            
            # Lấy tất cả achievements
            all_achievements = AchievementService.get_all_achievements()
            
            unlocked_achievements = []
            
            for achievement in all_achievements:
                achievement_id = achievement['achievement_id']
                condition_type = achievement['condition_type']
                condition_value = achievement['condition_value']
                
                # Kiểm tra xem user đã có achievement này chưa
                check_query = text('''
                    SELECT COUNT(*) as count 
                    FROM UserAchievements 
                    WHERE user_id = :user_id AND achievement_id = :achievement_id
                ''')
                check_result = db.session.execute(check_query, {
                    'user_id': user_id,
                    'achievement_id': achievement_id
                }).fetchone()
                
                if check_result and check_result.count > 0:
                    continue  # Đã có rồi, bỏ qua
                
                # Kiểm tra điều kiện
                condition_met = False
                
                if condition_type == 'TOTAL_POINTS' and points >= condition_value:
                    condition_met = True
                elif condition_type == 'CORRECT_PREDICTIONS' and correct_predictions >= condition_value:
                    condition_met = True
                elif condition_type == 'TOTAL_PREDICTIONS' and total_predictions >= condition_value:
                    condition_met = True
                elif condition_type == 'PERFECT_PREDICTIONS':
                    # Cần thêm logic cho perfect predictions
                    pass
                
                if condition_met:
                    # Mở khóa achievement
                    unlock_query = text('''
                        INSERT INTO UserAchievements (user_id, achievement_id)
                        VALUES (:user_id, :achievement_id)
                    ''')
                    db.session.execute(unlock_query, {
                        'user_id': user_id,
                        'achievement_id': achievement_id
                    })
                    
                    # Cộng điểm thưởng
                    points_reward = achievement.get('points_reward', 0)
                    if points_reward > 0:
                        update_points_query = text('''
                            UPDATE Users 
                            SET points = points + :points 
                            WHERE user_id = :user_id
                        ''')
                        db.session.execute(update_points_query, {
                            'user_id': user_id,
                            'points': points_reward
                        })
                    
                    unlocked_achievements.append(achievement)
            
            db.session.commit()
            return unlocked_achievements
        except Exception as e:
            print(f"ERROR in check_and_unlock_achievements: {str(e)}")
            db.session.rollback()
            return []