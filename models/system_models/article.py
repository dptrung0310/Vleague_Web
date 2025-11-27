from datetime import datetime

from extensions import db

class Article(db.Model):
    """Mô hình Bài báo"""
    __tablename__ = 'Articles'
    article_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True)  # Dùng cho URL thân thiện
    content = db.Column(db.Text, nullable=False)
    thumbnail_url = db.Column(db.String(255))
    author_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Có thể liên kết bài viết với trận đấu hoặc đội bóng
    related_match_id = db.Column(db.Integer, db.ForeignKey('Matches.match_id'), nullable=True)

    def to_dict(self):
        return {
            'article_id': self.article_id,
            'title': self.title,
            'slug': self.slug,
            'content': self.content,
            'thumbnail_url': self.thumbnail_url,
            'author_id': self.author_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'related_match_id': self.related_match_id
        }
