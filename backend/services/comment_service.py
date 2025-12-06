from extensions import db
from sqlalchemy import text
from datetime import datetime

class CommentService:
    @staticmethod
    def get_all_comments():
        try:
            query = text('''
                SELECT c.*, u.username, u.avatar_url, p.title as post_title
                FROM Comments c
                LEFT JOIN Users u ON c.user_id = u.user_id
                LEFT JOIN Posts p ON c.post_id = p.post_id
                ORDER BY c.created_at DESC
            ''')
            result = db.session.execute(query)
            
            comments = []
            for row in result:
                comment_dict = dict(row._mapping)
                
                for field in ['created_at', 'updated_at']:
                    if comment_dict.get(field):
                        if isinstance(comment_dict[field], str):
                            try:
                                comment_dict[field] = datetime.strptime(
                                    comment_dict[field], '%Y-%m-%d %H:%M:%S'
                                ).isoformat()
                            except:
                                comment_dict[field] = None
                        elif hasattr(comment_dict[field], 'isoformat'):
                            comment_dict[field] = comment_dict[field].isoformat()
                
                comments.append(comment_dict)
            
            return comments
        except Exception as e:
            print(f"ERROR in get_all_comments: {str(e)}")
            return []
    
    @staticmethod
    def get_comment_by_id(comment_id):
        try:
            query = text('''
                SELECT c.*, u.username, u.avatar_url
                FROM Comments c
                LEFT JOIN Users u ON c.user_id = u.user_id
                WHERE c.comment_id = :id
            ''')
            result = db.session.execute(query, {'id': comment_id}).fetchone()
            
            if result:
                comment_dict = dict(result._mapping)
                
                for field in ['created_at', 'updated_at']:
                    if comment_dict.get(field):
                        if isinstance(comment_dict[field], str):
                            try:
                                comment_dict[field] = datetime.strptime(
                                    comment_dict[field], '%Y-%m-%d %H:%M:%S'
                                ).isoformat()
                            except:
                                comment_dict[field] = None
                        elif hasattr(comment_dict[field], 'isoformat'):
                            comment_dict[field] = comment_dict[field].isoformat()
                
                return comment_dict
            return None
        except Exception as e:
            print(f"ERROR in get_comment_by_id: {str(e)}")
            return None
    
    @staticmethod
    def create_comment(data):
        try:
            required_fields = ['user_id', 'post_id', 'content']
            for field in required_fields:
                if field not in data:
                    return None, f'{field} is required'
            
            query = text('''
                INSERT INTO Comments (user_id, post_id, content)
                VALUES (:user_id, :post_id, :content)
            ''')
            
            db.session.execute(query, data)
            db.session.commit()
            
            # Lấy ID vừa tạo
            last_id = db.session.execute(text('SELECT last_insert_rowid()')).fetchone()[0]
            
            return CommentService.get_comment_by_id(last_id), None
        except Exception as e:
            print(f"ERROR in create_comment: {str(e)}")
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def update_comment(comment_id, data):
        try:
            existing = CommentService.get_comment_by_id(comment_id)
            if not existing:
                return None, "Comment not found"
            
            # Kiểm tra xem user có quyền sửa comment không
            if 'user_id' in data and existing['user_id'] != data['user_id']:
                return None, "Unauthorized"
            
            set_clause = ', '.join([f"{key} = :{key}" for key in data.keys()])
            query = text(f'''
                UPDATE Comments 
                SET {set_clause}
                WHERE comment_id = :comment_id
            ''')
            
            params = data.copy()
            params['comment_id'] = comment_id
            
            db.session.execute(query, params)
            db.session.commit()
            
            return CommentService.get_comment_by_id(comment_id), None
        except Exception as e:
            print(f"ERROR in update_comment: {str(e)}")
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def delete_comment(comment_id):
        try:
            existing = CommentService.get_comment_by_id(comment_id)
            if not existing:
                return False, "Comment not found"
            
            query = text('DELETE FROM Comments WHERE comment_id = :comment_id')
            db.session.execute(query, {'comment_id': comment_id})
            db.session.commit()
            
            return True, None
        except Exception as e:
            print(f"ERROR in delete_comment: {str(e)}")
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def get_comments_by_post(post_id):
        try:
            query = text('''
                SELECT c.*, u.username, u.avatar_url
                FROM Comments c
                LEFT JOIN Users u ON c.user_id = u.user_id
                WHERE c.post_id = :post_id
                ORDER BY c.created_at ASC
            ''')
            
            result = db.session.execute(query, {'post_id': post_id})
            
            comments = []
            for row in result:
                comment_dict = dict(row._mapping)
                
                for field in ['created_at', 'updated_at']:
                    if comment_dict.get(field):
                        if isinstance(comment_dict[field], str):
                            try:
                                comment_dict[field] = datetime.strptime(
                                    comment_dict[field], '%Y-%m-%d %H:%M:%S'
                                ).isoformat()
                            except:
                                comment_dict[field] = None
                        elif hasattr(comment_dict[field], 'isoformat'):
                            comment_dict[field] = comment_dict[field].isoformat()
                
                comments.append(comment_dict)
            
            return comments
        except Exception as e:
            print(f"ERROR in get_comments_by_post: {str(e)}")
            return []
    
    @staticmethod
    def get_comments_by_user(user_id):
        try:
            query = text('''
                SELECT c.*, p.title as post_title
                FROM Comments c
                LEFT JOIN Posts p ON c.post_id = p.post_id
                WHERE c.user_id = :user_id
                ORDER BY c.created_at DESC
            ''')
            
            result = db.session.execute(query, {'user_id': user_id})
            
            comments = []
            for row in result:
                comment_dict = dict(row._mapping)
                
                for field in ['created_at', 'updated_at']:
                    if comment_dict.get(field):
                        if isinstance(comment_dict[field], str):
                            try:
                                comment_dict[field] = datetime.strptime(
                                    comment_dict[field], '%Y-%m-%d %H:%M:%S'
                                ).isoformat()
                            except:
                                comment_dict[field] = None
                        elif hasattr(comment_dict[field], 'isoformat'):
                            comment_dict[field] = comment_dict[field].isoformat()
                
                comments.append(comment_dict)
            
            return comments
        except Exception as e:
            print(f"ERROR in get_comments_by_user: {str(e)}")
            return []
    
    @staticmethod
    def get_comment_count_for_post(post_id):
        try:
            query = text('SELECT COUNT(*) as count FROM Comments WHERE post_id = :post_id')
            result = db.session.execute(query, {'post_id': post_id}).fetchone()
            
            return result.count if result else 0
        except Exception as e:
            print(f"ERROR in get_comment_count_for_post: {str(e)}")
            return 0
    
    @staticmethod
    def get_recent_comments(limit=10):
        try:
            query = text('''
                SELECT c.*, u.username, u.avatar_url, p.title as post_title
                FROM Comments c
                LEFT JOIN Users u ON c.user_id = u.user_id
                LEFT JOIN Posts p ON c.post_id = p.post_id
                ORDER BY c.created_at DESC
                LIMIT :limit
            ''')
            
            result = db.session.execute(query, {'limit': limit})
            
            comments = []
            for row in result:
                comment_dict = dict(row._mapping)
                
                for field in ['created_at', 'updated_at']:
                    if comment_dict.get(field):
                        if isinstance(comment_dict[field], str):
                            try:
                                comment_dict[field] = datetime.strptime(
                                    comment_dict[field], '%Y-%m-%d %H:%M:%S'
                                ).isoformat()
                            except:
                                comment_dict[field] = None
                        elif hasattr(comment_dict[field], 'isoformat'):
                            comment_dict[field] = comment_dict[field].isoformat()
                
                comments.append(comment_dict)
            
            return comments
        except Exception as e:
            print(f"ERROR in get_recent_comments: {str(e)}")
            return []