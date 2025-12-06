from extensions import db
from datetime import datetime

class Comment(db.Model):
    __tablename__ = 'Comments'
    
    comment_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('Posts.post_id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self, include_user=False):
        result = {
            'comment_id': self.comment_id,
            'user_id': self.user_id,
            'post_id': self.post_id,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_user and self.user:
            result['user'] = {
                'user_id': self.user.user_id,
                'username': self.user.username,
                'avatar_url': self.user.avatar_url
            }
        
        return result