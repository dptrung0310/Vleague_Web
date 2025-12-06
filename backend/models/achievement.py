from extensions import db
from datetime import datetime

class Achievement(db.Model):
    __tablename__ = 'Achievements'
    
    achievement_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon_url = db.Column(db.Text)
    condition_type = db.Column(db.String(50), nullable=False)  # 'TOTAL_POINTS', 'CORRECT_STREAK', etc.
    condition_value = db.Column(db.Integer, nullable=False)
    points_reward = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'achievement_id': self.achievement_id,
            'name': self.name,
            'description': self.description,
            'icon_url': self.icon_url,
            'condition_type': self.condition_type,
            'condition_value': self.condition_value,
            'points_reward': self.points_reward,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }