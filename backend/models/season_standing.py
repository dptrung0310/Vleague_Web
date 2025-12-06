from extensions import db

class SeasonStanding(db.Model):
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
    
    # Relationships
    season = db.relationship('Season', backref='standings')
    team = db.relationship('Team', backref='standings')
    
    __table_args__ = (
        db.UniqueConstraint('season_id', 'team_id', 'round', name='uq_season_team_round'),
    )
    
    def to_dict(self, include_related=False):
        result = {
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
        
        if include_related:
            if self.team:
                result['team'] = self.team.to_dict()
            if self.season:
                result['season'] = self.season.to_dict()
        
        return result