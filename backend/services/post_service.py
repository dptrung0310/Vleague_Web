from extensions import db
from sqlalchemy import text
from datetime import datetime

class PostService:
    @staticmethod
    def get_all_posts(include_counts=False):
        try:
            if include_counts:
                query = text('''
                    SELECT p.*, 
                           u.username, u.avatar_url,
                           COUNT(DISTINCT l.like_id) as like_count,
                           COUNT(DISTINCT c.comment_id) as comment_count
                    FROM Posts p
                    LEFT JOIN Users u ON p.user_id = u.user_id
                    LEFT JOIN Likes l ON p.post_id = l.post_id
                    LEFT JOIN Comments c ON p.post_id = c.post_id
                    GROUP BY p.post_id
                    ORDER BY p.created_at DESC
                ''')
            else:
                query = text('''
                    SELECT p.*, u.username, u.avatar_url
                    FROM Posts p
                    LEFT JOIN Users u ON p.user_id = u.user_id
                    ORDER BY p.created_at DESC
                ''')
            
            result = db.session.execute(query)
            
            posts = []
            for row in result:
                post_dict = dict(row._mapping)
                
                # Xử lý datetime
                for field in ['created_at', 'updated_at']:
                    if post_dict.get(field):
                        if isinstance(post_dict[field], str):
                            try:
                                post_dict[field] = datetime.strptime(
                                    post_dict[field], '%Y-%m-%d %H:%M:%S'
                                ).isoformat()
                            except:
                                post_dict[field] = None
                        elif hasattr(post_dict[field], 'isoformat'):
                            post_dict[field] = post_dict[field].isoformat()
                
                posts.append(post_dict)
            
            return posts
        except Exception as e:
            print(f"ERROR in get_all_posts: {str(e)}")
            return []
    
    @staticmethod
    def get_post_by_id(post_id, include_counts=False):
        try:
            if include_counts:
                query = text('''
                    SELECT p.*, 
                           u.username, u.avatar_url,
                           COUNT(DISTINCT l.like_id) as like_count,
                           COUNT(DISTINCT c.comment_id) as comment_count
                    FROM Posts p
                    LEFT JOIN Users u ON p.user_id = u.user_id
                    LEFT JOIN Likes l ON p.post_id = l.post_id
                    LEFT JOIN Comments c ON p.post_id = c.post_id
                    WHERE p.post_id = :id
                    GROUP BY p.post_id
                ''')
            else:
                query = text('''
                    SELECT p.*, u.username, u.avatar_url
                    FROM Posts p
                    LEFT JOIN Users u ON p.user_id = u.user_id
                    WHERE p.post_id = :id
                ''')
            
            result = db.session.execute(query, {'id': post_id}).fetchone()
            
            if result:
                post_dict = dict(result._mapping)
                
                for field in ['created_at', 'updated_at']:
                    if post_dict.get(field):
                        if isinstance(post_dict[field], str):
                            try:
                                post_dict[field] = datetime.strptime(
                                    post_dict[field], '%Y-%m-%d %H:%M:%S'
                                ).isoformat()
                            except:
                                post_dict[field] = None
                        elif hasattr(post_dict[field], 'isoformat'):
                            post_dict[field] = post_dict[field].isoformat()
                
                return post_dict
            return None
        except Exception as e:
            print(f"ERROR in get_post_by_id: {str(e)}")
            return None
    
    @staticmethod
    def create_post(data):
        try:
            required_fields = ['user_id', 'content']
            for field in required_fields:
                if field not in data:
                    return None, f'{field} is required'
            
            columns = []
            values = []
            params = {}
            
            for key, value in data.items():
                columns.append(key)
                values.append(f":{key}")
                params[key] = value
            
            query = text(f'''
                INSERT INTO Posts ({', '.join(columns)})
                VALUES ({', '.join(values)})
            ''')
            
            db.session.execute(query, params)
            db.session.commit()
            
            # Lấy ID vừa tạo
            last_id = db.session.execute(text('SELECT last_insert_rowid()')).fetchone()[0]
            
            return PostService.get_post_by_id(last_id), None
        except Exception as e:
            print(f"ERROR in create_post: {str(e)}")
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def update_post(post_id, data):
        try:
            existing = PostService.get_post_by_id(post_id)
            if not existing:
                return None, "Post not found"
            
            # Kiểm tra xem user có quyền sửa post không (tùy chọn)
            # if 'user_id' in data and existing['user_id'] != data['user_id']:
            #     return None, "Unauthorized"
            
            set_clause = ', '.join([f"{key} = :{key}" for key in data.keys()])
            query = text(f'''
                UPDATE Posts 
                SET {set_clause}
                WHERE post_id = :post_id
            ''')
            
            params = data.copy()
            params['post_id'] = post_id
            
            db.session.execute(query, params)
            db.session.commit()
            
            return PostService.get_post_by_id(post_id), None
        except Exception as e:
            print(f"ERROR in update_post: {str(e)}")
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def delete_post(post_id):
        try:
            existing = PostService.get_post_by_id(post_id)
            if not existing:
                return False, "Post not found"
            
            query = text('DELETE FROM Posts WHERE post_id = :post_id')
            db.session.execute(query, {'post_id': post_id})
            db.session.commit()
            
            return True, None
        except Exception as e:
            print(f"ERROR in delete_post: {str(e)}")
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def get_posts_by_user(user_id, include_counts=False):
        try:
            if include_counts:
                query = text('''
                    SELECT p.*, 
                           u.username, u.avatar_url,
                           COUNT(DISTINCT l.like_id) as like_count,
                           COUNT(DISTINCT c.comment_id) as comment_count
                    FROM Posts p
                    LEFT JOIN Users u ON p.user_id = u.user_id
                    LEFT JOIN Likes l ON p.post_id = l.post_id
                    LEFT JOIN Comments c ON p.post_id = c.post_id
                    WHERE p.user_id = :user_id
                    GROUP BY p.post_id
                    ORDER BY p.created_at DESC
                ''')
            else:
                query = text('''
                    SELECT p.*, u.username, u.avatar_url
                    FROM Posts p
                    LEFT JOIN Users u ON p.user_id = u.user_id
                    WHERE p.user_id = :user_id
                    ORDER BY p.created_at DESC
                ''')
            
            result = db.session.execute(query, {'user_id': user_id})
            
            posts = []
            for row in result:
                post_dict = dict(row._mapping)
                
                for field in ['created_at', 'updated_at']:
                    if post_dict.get(field):
                        if isinstance(post_dict[field], str):
                            try:
                                post_dict[field] = datetime.strptime(
                                    post_dict[field], '%Y-%m-%d %H:%M:%S'
                                ).isoformat()
                            except:
                                post_dict[field] = None
                        elif hasattr(post_dict[field], 'isoformat'):
                            post_dict[field] = post_dict[field].isoformat()
                
                posts.append(post_dict)
            
            return posts
        except Exception as e:
            print(f"ERROR in get_posts_by_user: {str(e)}")
            return []
    
    @staticmethod
    def get_posts_by_match(match_id):
        try:
            query = text('''
                SELECT p.*, u.username, u.avatar_url
                FROM Posts p
                LEFT JOIN Users u ON p.user_id = u.user_id
                WHERE p.match_id = :match_id
                ORDER BY p.created_at DESC
            ''')
            
            result = db.session.execute(query, {'match_id': match_id})
            
            posts = []
            for row in result:
                post_dict = dict(row._mapping)
                
                for field in ['created_at', 'updated_at']:
                    if post_dict.get(field):
                        if isinstance(post_dict[field], str):
                            try:
                                post_dict[field] = datetime.strptime(
                                    post_dict[field], '%Y-%m-%d %H:%M:%S'
                                ).isoformat()
                            except:
                                post_dict[field] = None
                        elif hasattr(post_dict[field], 'isoformat'):
                            post_dict[field] = post_dict[field].isoformat()
                
                posts.append(post_dict)
            
            return posts
        except Exception as e:
            print(f"ERROR in get_posts_by_match: {str(e)}")
            return []
    
    @staticmethod
    def search_posts(keyword):
        try:
            query = text('''
                SELECT p.*, u.username, u.avatar_url
                FROM Posts p
                LEFT JOIN Users u ON p.user_id = u.user_id
                WHERE p.title LIKE :keyword OR p.content LIKE :keyword
                ORDER BY p.created_at DESC
            ''')
            
            result = db.session.execute(query, {'keyword': f'%{keyword}%'})
            
            posts = []
            for row in result:
                post_dict = dict(row._mapping)
                
                for field in ['created_at', 'updated_at']:
                    if post_dict.get(field):
                        if isinstance(post_dict[field], str):
                            try:
                                post_dict[field] = datetime.strptime(
                                    post_dict[field], '%Y-%m-%d %H:%M:%S'
                                ).isoformat()
                            except:
                                post_dict[field] = None
                        elif hasattr(post_dict[field], 'isoformat'):
                            post_dict[field] = post_dict[field].isoformat()
                
                posts.append(post_dict)
            
            return posts
        except Exception as e:
            print(f"ERROR in search_posts: {str(e)}")
            return []
    
    @staticmethod
    def get_trending_posts(limit=10):
        try:
            query = text('''
                SELECT p.*, 
                       u.username, u.avatar_url,
                       COUNT(DISTINCT l.like_id) as like_count,
                       COUNT(DISTINCT c.comment_id) as comment_count,
                       (COUNT(DISTINCT l.like_id) * 2 + COUNT(DISTINCT c.comment_id)) as engagement_score
                FROM Posts p
                LEFT JOIN Users u ON p.user_id = u.user_id
                LEFT JOIN Likes l ON p.post_id = l.post_id
                LEFT JOIN Comments c ON p.post_id = c.post_id
                WHERE p.created_at >= datetime('now', '-7 days')
                GROUP BY p.post_id
                ORDER BY engagement_score DESC, p.created_at DESC
                LIMIT :limit
            ''')
            
            result = db.session.execute(query, {'limit': limit})
            
            posts = []
            for row in result:
                post_dict = dict(row._mapping)
                
                for field in ['created_at', 'updated_at']:
                    if post_dict.get(field):
                        if isinstance(post_dict[field], str):
                            try:
                                post_dict[field] = datetime.strptime(
                                    post_dict[field], '%Y-%m-%d %H:%M:%S'
                                ).isoformat()
                            except:
                                post_dict[field] = None
                        elif hasattr(post_dict[field], 'isoformat'):
                            post_dict[field] = post_dict[field].isoformat()
                
                posts.append(post_dict)
            
            return posts
        except Exception as e:
            print(f"ERROR in get_trending_posts: {str(e)}")
            return []