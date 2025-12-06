from extensions import db
from datetime import datetime

class UserAchievement(db.Model):
    __tablename__ = 'UserAchievements'
    
    user_achievement_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('Achievements.achievement_id'), nullable=False)
    achieved_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    achievement = db.relationship('Achievement', backref='user_achievements')
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'achievement_id', name='unique_user_achievement'),
    )
    
    def to_dict(self):
        return {
            'user_achievement_id': self.user_achievement_id,
            'user_id': self.user_id,
            'achievement_id': self.achievement_id,
            'achieved_at': self.achieved_at.isoformat() if self.achieved_at else None,
            'achievement': self.achievement.to_dict() if self.achievement else None
        }