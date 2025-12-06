# services/user_service.py
from extensions import db
from sqlalchemy import text
from datetime import datetime
import re

class UserService:
    @staticmethod
    def get_all_users():
        """Lấy tất cả users"""
        try:
            query = text('''
                SELECT user_id, username, full_name, avatar_url, 
                       points, correct_predictions, total_predictions,
                       created_at
                FROM Users 
                ORDER BY points DESC
            ''')
            result = db.session.execute(query)
            
            users = []
            for row in result:
                user_dict = dict(row._mapping)
                if user_dict.get('created_at'):
                    if isinstance(user_dict['created_at'], str):
                        try:
                            user_dict['created_at'] = datetime.strptime(
                                user_dict['created_at'], '%Y-%m-%d %H:%M:%S'
                            ).isoformat()
                        except:
                            user_dict['created_at'] = None
                users.append(user_dict)
            
            return users
        except Exception as e:
            print(f"ERROR in get_all_users: {str(e)}")
            return []
    
    @staticmethod
    def get_user_by_id(user_id):
        """Lấy user theo ID"""
        try:
            query = text('''
                SELECT user_id, username, email, full_name, avatar_url, 
                       points, correct_predictions, total_predictions,
                       created_at, updated_at
                FROM Users 
                WHERE user_id = :id
            ''')
            result = db.session.execute(query, {'id': user_id}).fetchone()
            
            if result:
                user_dict = dict(result._mapping)
                for field in ['created_at', 'updated_at']:
                    if user_dict.get(field):
                        if isinstance(user_dict[field], str):
                            try:
                                user_dict[field] = datetime.strptime(
                                    user_dict[field], '%Y-%m-%d %H:%M:%S'
                                ).isoformat()
                            except:
                                user_dict[field] = None
                return user_dict
            return None
        except Exception as e:
            print(f"ERROR in get_user_by_id: {str(e)}")
            return None
    
    @staticmethod
    def register_user(username, email, password, full_name='', avatar_url=''):
        """Đăng ký user mới"""
        try:
            # Kiểm tra email đã tồn tại
            email_check = text('SELECT COUNT(*) as count FROM Users WHERE email = :email')
            email_result = db.session.execute(email_check, {'email': email}).fetchone()
            if email_result and email_result.count > 0:
                return None, "Email đã tồn tại"
            
            # Kiểm tra username đã tồn tại
            username_check = text('SELECT COUNT(*) as count FROM Users WHERE username = :username')
            username_result = db.session.execute(username_check, {'username': username}).fetchone()
            if username_result and username_result.count > 0:
                return None, "Username đã tồn tại"
            
            # Hash password
            from extensions import bcrypt
            password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            
            # Tạo user mới
            query = text('''
                INSERT INTO Users (username, email, password_hash, full_name, avatar_url)
                VALUES (:username, :email, :password_hash, :full_name, :avatar_url)
            ''')
            
            db.session.execute(query, {
                'username': username,
                'email': email,
                'password_hash': password_hash,
                'full_name': full_name,
                'avatar_url': avatar_url
            })
            db.session.commit()
            
            # Lấy user vừa tạo
            last_id = db.session.execute(text('SELECT last_insert_rowid()')).fetchone()[0]
            user = UserService.get_user_by_id(last_id)
            
            return user, None
        except Exception as e:
            db.session.rollback()
            print(f"ERROR in register_user: {str(e)}")
            return None, "Đăng ký thất bại"
    
    @staticmethod
    def authenticate_user(email, password):
        """Xác thực user"""
        try:
            # Lấy user bằng email
            query = text('''
                SELECT user_id, username, email, password_hash, full_name, avatar_url,
                       points, correct_predictions, total_predictions
                FROM Users 
                WHERE email = :email
            ''')
            result = db.session.execute(query, {'email': email}).fetchone()
            
            if not result:
                return None, "Email không tồn tại"
            
            user_dict = dict(result._mapping)
            
            # Kiểm tra password
            from extensions import bcrypt
            if not bcrypt.check_password_hash(user_dict['password_hash'], password):
                return None, "Mật khẩu không đúng"
            
            # Xóa password_hash trước khi trả về
            del user_dict['password_hash']
            
            return user_dict, None
        except Exception as e:
            print(f"ERROR in authenticate_user: {str(e)}")
            return None, "Đăng nhập thất bại"
    
    @staticmethod
    def update_user(user_id, data):
        """Cập nhật thông tin user"""
        try:
            # Kiểm tra user tồn tại
            user = UserService.get_user_by_id(user_id)
            if not user:
                return None, "User không tồn tại"
            
            # Nếu có email mới, kiểm tra email không trùng
            if 'email' in data and data['email'] != user['email']:
                email_check = text('SELECT COUNT(*) as count FROM Users WHERE email = :email')
                email_result = db.session.execute(email_check, {'email': data['email']}).fetchone()
                if email_result and email_result.count > 0:
                    return None, "Email đã tồn tại"
            
            # Nếu có username mới, kiểm tra username không trùng
            if 'username' in data and data['username'] != user['username']:
                username_check = text('SELECT COUNT(*) as count FROM Users WHERE username = :username')
                username_result = db.session.execute(username_check, {'username': data['username']}).fetchone()
                if username_result and username_result.count > 0:
                    return None, "Username đã tồn tại"
            
            # Nếu có password mới, hash password
            if 'password' in data:
                from extensions import bcrypt
                password_hash = bcrypt.generate_password_hash(data['password']).decode('utf-8')
                data['password_hash'] = password_hash
                del data['password']
            
            # Xây dựng câu query UPDATE
            set_clauses = []
            params = {'user_id': user_id}
            
            for key, value in data.items():
                if key != 'user_id':
                    set_clauses.append(f"{key} = :{key}")
                    params[key] = value
            
            if not set_clauses:
                return user, None
            
            query = text(f'''
                UPDATE Users 
                SET {', '.join(set_clauses)}
                WHERE user_id = :user_id
            ''')
            
            db.session.execute(query, params)
            db.session.commit()
            
            # Lấy thông tin user đã cập nhật
            updated_user = UserService.get_user_by_id(user_id)
            return updated_user, None
        except Exception as e:
            db.session.rollback()
            print(f"ERROR in update_user: {str(e)}")
            return None, "Cập nhật thất bại"
    
    @staticmethod
    def get_user_stats(user_id):
        """Lấy thống kê của user"""
        try:
            # Đếm số bài viết
            posts_query = text('SELECT COUNT(*) as count FROM Posts WHERE user_id = :user_id')
            posts_result = db.session.execute(posts_query, {'user_id': user_id}).fetchone()
            
            # Đếm số lượt like user đã nhận
            received_likes_query = text('''
                SELECT COUNT(*) as count 
                FROM Likes l
                JOIN Posts p ON l.post_id = p.post_id
                WHERE p.user_id = :user_id
            ''')
            received_likes_result = db.session.execute(received_likes_query, {'user_id': user_id}).fetchone()
            
            # Đếm số comment
            comments_query = text('SELECT COUNT(*) as count FROM Comments WHERE user_id = :user_id')
            comments_result = db.session.execute(comments_query, {'user_id': user_id}).fetchone()
            
            # Đếm số dự đoán
            predictions_query = text('SELECT COUNT(*) as count FROM Predictions WHERE user_id = :user_id')
            predictions_result = db.session.execute(predictions_query, {'user_id': user_id}).fetchone()
            
            # Xếp hạng
            rank_query = text('''
                SELECT COUNT(*) + 1 as rank
                FROM Users 
                WHERE points > (SELECT points FROM Users WHERE user_id = :user_id)
            ''')
            rank_result = db.session.execute(rank_query, {'user_id': user_id}).fetchone()
            
            stats = {
                'user_id': user_id,
                'posts_count': posts_result.count if posts_result else 0,
                'received_likes_count': received_likes_result.count if received_likes_result else 0,
                'comments_count': comments_result.count if comments_result else 0,
                'predictions_count': predictions_result.count if predictions_result else 0,
                'rank': rank_result.rank if rank_result else 1
            }
            
            return stats, None
        except Exception as e:
            print(f"ERROR in get_user_stats: {str(e)}")
            return None, "Không thể lấy thống kê"
    
    @staticmethod
    def update_user_points(user_id, points_to_add, is_correct=False):
        """Cập nhật điểm cho user"""
        try:
            query = text('''
                UPDATE Users 
                SET points = points + :points,
                    total_predictions = total_predictions + 1,
                    correct_predictions = correct_predictions + :correct_increment
                WHERE user_id = :user_id
            ''')
            
            params = {
                'user_id': user_id,
                'points': points_to_add,
                'correct_increment': 1 if is_correct else 0
            }
            
            db.session.execute(query, params)
            db.session.commit()
            
            return True, None
        except Exception as e:
            db.session.rollback()
            print(f"ERROR in update_user_points: {str(e)}")
            return False, "Không thể cập nhật điểm"
    
    @staticmethod
    def get_leaderboard(limit=20):
        """Lấy bảng xếp hạng"""
        try:
            query = text('''
                SELECT user_id, username, avatar_url, points, 
                       correct_predictions, total_predictions,
                       ROW_NUMBER() OVER (ORDER BY points DESC) as rank
                FROM Users 
                ORDER BY points DESC
                LIMIT :limit
            ''')
            
            result = db.session.execute(query, {'limit': limit})
            
            leaderboard = []
            for row in result:
                leaderboard.append(dict(row._mapping))
            
            return leaderboard, None
        except Exception as e:
            print(f"ERROR in get_leaderboard: {str(e)}")
            return [], "Không thể lấy bảng xếp hạng"