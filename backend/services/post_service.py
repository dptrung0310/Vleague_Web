# services/post_service.py
import os
import time
from werkzeug.utils import secure_filename
from flask import current_app
from extensions import db
from models.post import Post
from models.like import Like
from models.comment import Comment
from sqlalchemy import or_ # <-- Nhớ import thêm or_
from models.user import User # <-- Import model User để join bảng

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class PostService:
    
    @staticmethod
    def create_post(user_id, form_data, file_storage):
        try:
            # 1. Lấy dữ liệu Text
            title = form_data.get('title')
            content = form_data.get('content')
            
            # Lấy ID tag
            match_id = form_data.get('match_id') or None
            team_id = form_data.get('team_id') or None
            player_id = form_data.get('player_id') or None

            # 2. Xử lý Upload ảnh
            image_url = None
            if file_storage and allowed_file(file_storage.filename):
                filename = secure_filename(file_storage.filename)
                new_filename = f"post_{user_id}_{int(time.time())}.{filename.rsplit('.', 1)[1].lower()}"
                
                upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER_POSTS'], 'posts')
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                    
                file_storage.save(os.path.join(upload_folder, new_filename))
                image_url = f"/static/uploads/posts/posts/{new_filename}"

            # 3. Lưu vào DB
            new_post = Post(
                user_id=user_id,
                title=title,
                content=content,
                image_url=image_url,
                match_id=match_id,
                team_id=team_id,
                player_id=player_id
            )
            
            db.session.add(new_post)
            db.session.commit()
            
            # Trả về data đầy đủ để frontend hiển thị ngay mà không bị lỗi thiếu field
            result_data = new_post.to_dict()
            result_data['comments'] = []
            result_data['comment_count'] = 0
            result_data['like_count'] = 0
            result_data['is_liked'] = False
            
            return result_data, None
        except Exception as e:
            db.session.rollback()
            print("Error creating post:", str(e))
            return None, str(e)

    @staticmethod
    def get_all_posts(page=1, per_page=10, current_user_id=None, search_query=None):
        try:
            # Bắt đầu query cơ bản
            query = Post.query

            # --- LOGIC TÌM KIẾM MỚI ---
            if search_query:
                # Cần join với bảng User để tìm theo tên người đăng
                query = query.join(User)
                search_term = f"%{search_query}%"
                query = query.filter(
                    or_(
                        Post.title.like(search_term),       # Tìm theo tiêu đề
                        Post.content.like(search_term),     # Tìm theo nội dung
                        User.username.like(search_term),    # Tìm theo username
                        User.full_name.like(search_term)    # Tìm theo tên đầy đủ (nếu có cột này)
                    )
                )
            # ---------------------------

            # Sắp xếp bài mới nhất trước
            pagination = query.order_by(Post.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            posts_data = []
            
            for post in pagination.items:
                # ... (Phần code xử lý to_dict, comments, likes giữ nguyên y hệt cũ) ...
                # Copy lại nguyên khối logic xử lý data ở đây từ file cũ của bạn
                data = post.to_dict(current_user_id)
                
                # Query Comment
                comments = Comment.query.filter_by(post_id=post.post_id).order_by(Comment.created_at.asc()).all()
                data['comments'] = [c.to_dict(include_user=True) for c in comments]
                data['comment_count'] = len(comments)

                # Query Like
                like_count = Like.query.filter_by(post_id=post.post_id).count()
                data['like_count'] = like_count

                # Check is_liked
                is_liked = False
                if current_user_id:
                    check_like = Like.query.filter_by(user_id=current_user_id, post_id=post.post_id).first()
                    if check_like: is_liked = True
                data['is_liked'] = is_liked
                
                posts_data.append(data)
            
            return {
                'posts': posts_data,
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page
            }, None
        except Exception as e:
            return None, str(e)
    @staticmethod
    def toggle_like(user_id, post_id):
        try:
            existing_like = Like.query.filter_by(user_id=user_id, post_id=post_id).first()
            
            action = ''
            if existing_like:
                db.session.delete(existing_like)
                action = 'unliked'
            else:
                new_like = Like(user_id=user_id, post_id=post_id)
                db.session.add(new_like)
                action = 'liked'
                
            db.session.commit()
            return action, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def add_comment(user_id, post_id, content):
        try:
            if not content or not content.strip():
                return None, "Nội dung bình luận không được để trống"
                
            new_comment = Comment(user_id=user_id, post_id=post_id, content=content)
            db.session.add(new_comment)
            db.session.commit()
            
            return new_comment.to_dict(include_user=True), None
        except Exception as e:
            return None, str(e)
            
    @staticmethod
    def get_post_detail(post_id, current_user_id=None):
        try:
            post = Post.query.get(post_id)
            if not post:
                return None, "Bài viết không tồn tại"
            
            data = post.to_dict(current_user_id)
            
            # Lấy comment
            comments = Comment.query.filter_by(post_id=post_id)\
                .order_by(Comment.created_at.desc()).all()
            data['comments'] = [c.to_dict(include_user=True) for c in comments]
            
            # Lấy like count
            data['like_count'] = Like.query.filter_by(post_id=post_id).count()
            
            # Check is liked
            if current_user_id:
                check = Like.query.filter_by(user_id=current_user_id, post_id=post_id).first()
                data['is_liked'] = True if check else False
            else:
                data['is_liked'] = False

            return data, None
        except Exception as e:
            return None, str(e)
        
    @staticmethod
    def delete_post(user_id, post_id):
        try:
            post = Post.query.get(post_id)
            
            if not post:
                return None, "Bài viết không tồn tại"
            
            if str(post.user_id) != str(user_id):
                return None, "Bạn không có quyền xóa bài viết này"

            if post.image_url:
                try:
                    relative_path = post.image_url.lstrip('/')
                    filename = os.path.basename(post.image_url)
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER_POSTS'], 'posts', filename)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except Exception as e:
                    print(f"Lỗi xóa ảnh: {e}") 

            db.session.delete(post)
            db.session.commit()
            
            return "Xóa bài viết thành công", None

        except Exception as e:
            db.session.rollback()
            return None, str(e)