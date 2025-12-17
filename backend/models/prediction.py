from extensions import db
from datetime import datetime

class Prediction(db.Model):
    __tablename__ = 'Predictions'
    
    prediction_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('Matches.match_id'), nullable=False)
    
    # Giai đoạn 1: Dự đoán kết quả
    predicted_result = db.Column(db.String(10))  # 'HOME_WIN', 'DRAW', 'AWAY_WIN'
    
    # Giai đoạn 2: Dự đoán tỉ số
    predicted_home_score = db.Column(db.Integer, nullable=True)  # Thêm nullable=True
    predicted_away_score = db.Column(db.Integer, nullable=True)  # Thêm nullable=True
    
    # Giai đoạn 3: Dự đoán thẻ phạt (NEW)
    # Giá trị: 'OVER_3.5' hoặc 'UNDER_3.5'
    predicted_card_over_under = db.Column(db.String(20), nullable=True)
    
    # Điểm thưởng
    points_awarded = db.Column(db.Integer, default=0)
    
    # Trạng thái
    status = db.Column(db.String(20), default='PENDING')  # 'PENDING', 'CORRECT', 'INCORRECT', 'PROCESSED'
    
    # Thời gian
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship với Match
    match = db.relationship('Match', backref='predictions')
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'match_id', name='unique_user_match_prediction'),
    )
    
    def to_dict(self, include_match=False):
        result = {
            'prediction_id': self.prediction_id,
            'user_id': self.user_id,
            'match_id': self.match_id,
            'predicted_result': self.predicted_result,
            'predicted_home_score': self.predicted_home_score,
            'predicted_away_score': self.predicted_away_score,
            'predicted_card_over_under': self.predicted_card_over_under, 
            'points_awarded': self.points_awarded,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_match and self.match:
            result['match'] = {
                'match_id': self.match.match_id,
                'home_team_id': self.match.home_team_id,
                'away_team_id': self.match.away_team_id,
                'match_datetime': self.match.match_datetime.isoformat() if self.match.match_datetime else None,
                'status': self.match.status,
                'home_score': self.match.home_score,
                'away_score': self.match.away_score
            }
        
        return result
    def get_match_info(self):
        """Lấy thông tin trận đấu liên quan"""
        if self.match:
            return {
                'home_team': self.match.home_team.name if self.match.home_team else None,
                'away_team': self.match.away_team.name if self.match.away_team else None,
                'match_datetime': self.match.match_datetime.isoformat() if self.match.match_datetime else None,
                'status': self.match.status,
                'actual_home_score': self.match.home_score,
                'actual_away_score': self.match.away_score
            }
        return None