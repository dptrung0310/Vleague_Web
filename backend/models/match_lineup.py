from extensions import db

class MatchLineup(db.Model):
    __tablename__ = 'MatchLineups'
    
    lineup_id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('Matches.match_id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('Teams.team_id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('Players.player_id'), nullable=False)
    is_starter = db.Column(db.Boolean, nullable=False, default=False)
    shirt_number = db.Column(db.Integer, nullable=False)
    position = db.Column(db.String(50))
    
    # Relationships
    team = db.relationship('Team', backref='lineups')
    player = db.relationship('Player', backref='match_appearances')
    
    __table_args__ = (
        db.UniqueConstraint('match_id', 'player_id', name='unique_match_player'),
    )