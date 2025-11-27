from sqlalchemy import UniqueConstraint

from extensions import db

class MatchReferee(db.Model):
    """Mô hình Trọng tài trận đấu"""
    __tablename__ = 'Match_Referees'
    match_referee_id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('Matches.match_id'), nullable=False)
    referee_id = db.Column(db.Integer, db.ForeignKey('Referees.referee_id'), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    __table_args__ = (UniqueConstraint('match_id', 'referee_id', 'role'),)

    referee = db.relationship('Referee', backref='match_assignments')

    def to_dict(self):
        return {
            'match_referee_id': self.match_referee_id,
            'match_id': self.match_id,
            'referee_id': self.referee_id,
            'role': self.role
        }
