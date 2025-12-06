from extensions import db

class MatchEvent(db.Model):
    __tablename__ = 'MatchEvents'
    
    event_id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('Matches.match_id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('Teams.team_id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('Players.player_id'), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    minute = db.Column(db.Integer, nullable=False)
    
    # Relationships
    team = db.relationship('Team', backref='match_events')
    player = db.relationship('Player', backref='match_events')