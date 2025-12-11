# models/post.py
from extensions import db
from datetime import datetime

class Post(db.Model):
    __tablename__ = 'Posts'
    
    post_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    
    # Nội dung chính
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    image_url = db.Column(db.Text) # Đường dẫn ảnh (nếu có)
    
    # Gắn thẻ (Tag) - Cho phép null nếu là bài viết vu vơ
    match_id = db.Column(db.Integer, db.ForeignKey('Matches.match_id'), nullable=True)
    team_id = db.Column(db.Integer, db.ForeignKey('Teams.team_id'), nullable=True)
    player_id = db.Column(db.Integer, db.ForeignKey('Players.player_id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Quan hệ (Relationships)
    # user = db.relationship('User', backref='posts')
    match = db.relationship('Match', backref='posts')
    team = db.relationship('Team', backref='posts')
    player = db.relationship('Player', backref='posts')
    
    # Cascade delete: Xóa bài thì xóa luôn Like/Comment
    likes = db.relationship('Like', backref='post', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='post', cascade='all, delete-orphan')
    
    def to_dict(self, current_user_id=None):
        result = {
            'post_id': self.post_id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'like_count': len(self.likes),
            'comment_count': len(self.comments),
        }
        
        # Info người đăng
        if self.user:
            result['user'] = {
                'user_id': self.user.user_id,
                'username': self.user.username,
                'full_name': getattr(self.user, 'full_name', self.user.username),
                'avatar_url': self.user.avatar_url
            }

        # Check xem user hiện tại đã like bài này chưa
        result['is_liked'] = False
        if current_user_id:
            for like in self.likes:
                if like.user_id == current_user_id:
                    result['is_liked'] = True
                    break

        # Info đối tượng được tag (nếu có)
        if self.match_id and self.match:
            result['match'] = {'match_id': self.match.match_id, 'name': f"Match #{self.match.match_id}"}
        if self.team_id and self.team:
            result['team'] = {'team_id': self.team.team_id, 'name': self.team.name}
        if self.player_id and self.player:
            result['player'] = {'player_id': self.player.player_id, 'name': self.player.name}
            
        return result