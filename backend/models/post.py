from extensions import db
from datetime import datetime

class Post(db.Model):
    __tablename__ = 'Posts'
    
    post_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    image_url = db.Column(db.Text)
    match_id = db.Column(db.Integer, db.ForeignKey('Matches.match_id'))
    post_type = db.Column(db.String(20), default='GENERAL')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    match = db.relationship('Match', backref='posts')
    likes = db.relationship('Like', backref='post', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='post', cascade='all, delete-orphan')
    
    def to_dict(self, include_user=False, include_match=False, include_counts=False):
        result = {
            'post_id': self.post_id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'image_url': self.image_url,
            'match_id': self.match_id,
            'post_type': self.post_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_user and self.user:
            result['user'] = {
                'user_id': self.user.user_id,
                'username': self.user.username,
                'avatar_url': self.user.avatar_url
            }
        
        if include_match and self.match:
            result['match'] = {
                'match_id': self.match.match_id,
                'home_team_id': self.match.home_team_id,
                'away_team_id': self.match.away_team_id
            }
        
        if include_counts:
            result['like_count'] = len(self.likes)
            result['comment_count'] = len(self.comments)
        
        return result