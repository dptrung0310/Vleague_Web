from extensions import db

class MatchEvent(db.Model):
    """Mô hình Sự kiện trong trận đấu"""
    __tablename__ = 'MatchEvents'
    event_id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('Matches.match_id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('Teams.team_id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('Players.player_id'), nullable=False)
    event_type = db.Column(db.String(50), nullable=False) # Goal, Card, etc.
    minute = db.Column(db.Integer, nullable=False)

    team = db.relationship('Team')
    player = db.relationship('Player')

    def to_dict(self):
        return {
            'event_id': self.event_id,
            'match_id': self.match_id,
            'team_id': self.team_id,
            'player_id': self.player_id,
            'event_type': self.event_type,
            'minute': self.minute
        }
