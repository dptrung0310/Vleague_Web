# models/user.py
from extensions import db, bcrypt
from datetime import datetime

class User(db.Model):
    __tablename__ = 'Users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100))
    avatar_url = db.Column(db.Text, default='')
    points = db.Column(db.Integer, default=0)
    correct_predictions = db.Column(db.Integer, default=0)
    total_predictions = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    google_id = db.Column(db.String(100), unique=True, nullable=True) # Thêm dòng này
    
    # Relationships
    predictions = db.relationship('Prediction', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    posts = db.relationship('Post', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    achievements = db.relationship('UserAchievement', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash và lưu password"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Kiểm tra password"""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Chuyển đổi thành dictionary"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'avatar_url': self.avatar_url,
            'points': self.points,
            'correct_predictions': self.correct_predictions,
            'total_predictions': self.total_predictions,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_public_dict(self):
        """Thông tin công khai (không có email)"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'full_name': self.full_name,
            'avatar_url': self.avatar_url,
            'points': self.points,
            'correct_predictions': self.correct_predictions,
            'total_predictions': self.total_predictions
        }