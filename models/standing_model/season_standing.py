from sqlalchemy import UniqueConstraint

from extensions import db

class SeasonStanding(db.Model):
    """Mô hình Bảng xếp hạng mùa giải"""
    __tablename__ = 'SeasonStandings'
    standing_id = db.Column(db.Integer, primary_key=True)
    season_id = db.Column(db.Integer, db.ForeignKey('Seasons.season_id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('Teams.team_id'), nullable=False)
    round = db.Column(db.Integer, nullable=False)
    position = db.Column(db.Integer, nullable=False)
    played = db.Column(db.Integer, nullable=False)
    wins = db.Column(db.Integer, nullable=False)
    draws = db.Column(db.Integer, nullable=False)
    losses = db.Column(db.Integer, nullable=False)
    goals_for = db.Column(db.Integer, nullable=False)
    goals_against = db.Column(db.Integer, nullable=False)
    goal_difference = db.Column(db.Integer, nullable=False)
    points = db.Column(db.Integer, nullable=False)

    __table_args__ = (UniqueConstraint('season_id', 'team_id', 'round'),)

    team = db.relationship('Team')

    def to_dict(self):
        return {
            'standing_id': self.standing_id,
            'season_id': self.season_id,
            'team_id': self.team_id,
            'round': self.round,
            'position': self.position,
            'played': self.played,
            'wins': self.wins,
            'draws': self.draws,
            'losses': self.losses,
            'goals_for': self.goals_for,
            'goals_against': self.goals_against,
            'goal_difference': self.goal_difference,
            'points': self.points
        }