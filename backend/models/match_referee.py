from extensions import db

class MatchReferee(db.Model):
    __tablename__ = 'Match_Referees'
    
    match_referee_id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('Matches.match_id'), nullable=False)
    referee_id = db.Column(db.Integer, db.ForeignKey('Referees.referee_id'), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    
    # Relationship
    referee = db.relationship('Referee', backref='match_assignments')
    
    __table_args__ = (
        db.UniqueConstraint('match_id', 'referee_id', 'role', name='unique_match_referee_role'),
    )