from sqlalchemy import UniqueConstraint

from extensions import db

class TeamRoster(db.Model):
    """Mô hình Danh sách đội"""
    __tablename__ = 'TeamRosters'
    roster_id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('Players.player_id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('Teams.team_id'), nullable=False)
    season_id = db.Column(db.Integer, db.ForeignKey('Seasons.season_id'), nullable=False)
    shirt_number = db.Column(db.Integer)

    __table_args__ = (
        UniqueConstraint('player_id', 'season_id', name='uk_player_season'),
        UniqueConstraint('team_id', 'season_id', 'shirt_number', name='uk_team_season_shirt'),
    )

    def to_dict(self):
        return {
            'roster_id': self.roster_id,
            'player_id': self.player_id,
            'team_id': self.team_id,
            'season_id': self.season_id,
            'shirt_number': self.shirt_number
        }