from sqlalchemy import UniqueConstraint

from extensions import db

class MatchLineup(db.Model):
    """Mô hình Lineup trận đấu"""
    __tablename__ = 'MatchLineups'
    lineup_id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('Matches.match_id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('Teams.team_id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('Players.player_id'), nullable=False)
    is_starter = db.Column(db.Boolean, nullable=False)
    shirt_number = db.Column(db.Integer, nullable=False)
    position = db.Column(db.String(50))

    __table_args__ = (UniqueConstraint('match_id', 'player_id'),)

    team = db.relationship('Team')
    player = db.relationship('Player')

    def to_dict(self):
        return {
            'lineup_id': self.lineup_id,
            'match_id': self.match_id,
            'team_id': self.team_id,
            'player_id': self.player_id,
            'is_starter': self.is_starter,
            'shirt_number': self.shirt_number,
            'position': self.position
        }
