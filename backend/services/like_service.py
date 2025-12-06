from extensions import db
from sqlalchemy import text
from datetime import datetime

class LikeService:
    @staticmethod
    def get_all_likes():
        try:
            query = text('''
                SELECT l.*, u.username, p.title as post_title
                FROM Likes l
                LEFT JOIN Users u ON l.user_id = u.user_id
                LEFT JOIN Posts p ON l.post_id = p.post_id
                ORDER BY l.created_at DESC
            ''')
            result = db.session.execute(query)
            
            likes = []
            for row in result:
                like_dict = dict(row._mapping)
                
                if like_dict.get('created_at'):
                    if isinstance(like_dict['created_at'], str):
                        try:
                            like_dict['created_at'] = datetime.strptime(
                                like_dict['created_at'], '%Y-%m-%d %H:%M:%S'
                            ).isoformat()
                        except:
                            like_dict['created_at'] = None
                    elif hasattr(like_dict['created_at'], 'isoformat'):
                        like_dict['created_at'] = like_dict['created_at'].isoformat()
                
                likes.append(like_dict)
            
            return likes
        except Exception as e:
            print(f"ERROR in get_all_likes: {str(e)}")
            return []
    
    @staticmethod
    def get_like_by_id(like_id):
        try:
            query = text('SELECT * FROM Likes WHERE like_id = :id')
            result = db.session.execute(query, {'id': like_id}).fetchone()
            
            if result:
                like_dict = dict(result._mapping)
                
                if like_dict.get('created_at'):
                    if isinstance(like_dict['created_at'], str):
                        try:
                            like_dict['created_at'] = datetime.strptime(
                                like_dict['created_at'], '%Y-%m-%d %H:%M:%S'
                            ).isoformat()
                        except:
                            like_dict['created_at'] = None
                    elif hasattr(like_dict['created_at'], 'isoformat'):
                        like_dict['created_at'] = like_dict['created_at'].isoformat()
                
                return like_dict
            return None
        except Exception as e:
            print(f"ERROR in get_like_by_id: {str(e)}")
            return None
    
    @staticmethod
    def create_like(data):
        try:
            required_fields = ['user_id', 'post_id']
            for field in required_fields:
                if field not in data:
                    return None, f'{field} is required'
            
            # Kiểm tra xem đã like chưa
            check_query = text('''
                SELECT COUNT(*) as count 
                FROM Likes 
                WHERE user_id = :user_id AND post_id = :post_id
            ''')
            check_result = db.session.execute(check_query, {
                'user_id': data['user_id'],
                'post_id': data['post_id']
            }).fetchone()
            
            if check_result and check_result.count > 0:
                return None, "Already liked"
            
            query = text('''
                INSERT INTO Likes (user_id, post_id)
                VALUES (:user_id, :post_id)
            ''')
            
            db.session.execute(query, data)
            db.session.commit()
            
            # Lấy ID vừa tạo
            last_id = db.session.execute(text('SELECT last_insert_rowid()')).fetchone()[0]
            
            return LikeService.get_like_by_id(last_id), None
        except Exception as e:
            print(f"ERROR in create_like: {str(e)}")
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def delete_like(like_id):
        try:
            existing = LikeService.get_like_by_id(like_id)
            if not existing:
                return False, "Like not found"
            
            query = text('DELETE FROM Likes WHERE like_id = :like_id')
            db.session.execute(query, {'like_id': like_id})
            db.session.commit()
            
            return True, None
        except Exception as e:
            print(f"ERROR in delete_like: {str(e)}")
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def unlike_post(user_id, post_id):
        try:
            query = text('''
                DELETE FROM Likes 
                WHERE user_id = :user_id AND post_id = :post_id
            ''')
            
            result = db.session.execute(query, {
                'user_id': user_id,
                'post_id': post_id
            })
            
            db.session.commit()
            
            return result.rowcount > 0, None
        except Exception as e:
            print(f"ERROR in unlike_post: {str(e)}")
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def get_likes_by_post(post_id):
        try:
            query = text('''
                SELECT l.*, u.username, u.avatar_url
                FROM Likes l
                LEFT JOIN Users u ON l.user_id = u.user_id
                WHERE l.post_id = :post_id
                ORDER BY l.created_at DESC
            ''')
            
            result = db.session.execute(query, {'post_id': post_id})
            
            likes = []
            for row in result:
                like_dict = dict(row._mapping)
                
                if like_dict.get('created_at'):
                    if isinstance(like_dict['created_at'], str):
                        try:
                            like_dict['created_at'] = datetime.strptime(
                                like_dict['created_at'], '%Y-%m-%d %H:%M:%S'
                            ).isoformat()
                        except:
                            like_dict['created_at'] = None
                    elif hasattr(like_dict['created_at'], 'isoformat'):
                        like_dict['created_at'] = like_dict['created_at'].isoformat()
                
                likes.append(like_dict)
            
            return likes
        except Exception as e:
            print(f"ERROR in get_likes_by_post: {str(e)}")
            return []
    
    @staticmethod
    def get_likes_by_user(user_id):
        try:
            query = text('''
                SELECT l.*, p.title, p.content
                FROM Likes l
                LEFT JOIN Posts p ON l.post_id = p.post_id
                WHERE l.user_id = :user_id
                ORDER BY l.created_at DESC
            ''')
            
            result = db.session.execute(query, {'user_id': user_id})
            
            likes = []
            for row in result:
                like_dict = dict(row._mapping)
                
                if like_dict.get('created_at'):
                    if isinstance(like_dict['created_at'], str):
                        try:
                            like_dict['created_at'] = datetime.strptime(
                                like_dict['created_at'], '%Y-%m-%d %H:%M:%S'
                            ).isoformat()
                        except:
                            like_dict['created_at'] = None
                    elif hasattr(like_dict['created_at'], 'isoformat'):
                        like_dict['created_at'] = like_dict['created_at'].isoformat()
                
                likes.append(like_dict)
            
            return likes
        except Exception as e:
            print(f"ERROR in get_likes_by_user: {str(e)}")
            return []
    
    @staticmethod
    def is_post_liked_by_user(user_id, post_id):
        try:
            query = text('''
                SELECT COUNT(*) as count 
                FROM Likes 
                WHERE user_id = :user_id AND post_id = :post_id
            ''')
            
            result = db.session.execute(query, {
                'user_id': user_id,
                'post_id': post_id
            }).fetchone()
            
            return result.count > 0 if result else False
        except Exception as e:
            print(f"ERROR in is_post_liked_by_user: {str(e)}")
            return False
    
    @staticmethod
    def get_like_count_for_post(post_id):
        try:
            query = text('SELECT COUNT(*) as count FROM Likes WHERE post_id = :post_id')
            result = db.session.execute(query, {'post_id': post_id}).fetchone()
            
            return result.count if result else 0
        except Exception as e:
            print(f"ERROR in get_like_count_for_post: {str(e)}")
            return 0