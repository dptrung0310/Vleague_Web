from extensions import db

class TeamRoster(db.Model):
    __tablename__ = 'TeamRosters'
    
    roster_id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('Players.player_id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('Teams.team_id'), nullable=False)
    season_id = db.Column(db.Integer, db.ForeignKey('Seasons.season_id'), nullable=False)
    shirt_number = db.Column(db.Integer)
    
    # Relationships
    player = db.relationship('Player', backref='team_rosters')
    team = db.relationship('Team', backref='team_rosters')
    season = db.relationship('Season', backref='team_rosters')
    
    __table_args__ = (
        db.UniqueConstraint('player_id', 'season_id', name='uk_player_season'),
        db.UniqueConstraint('team_id', 'season_id', 'shirt_number', name='uk_team_season_shirt'),
    )
    
    def to_dict(self, include_related=False):
        result = {
            'roster_id': self.roster_id,
            'player_id': self.player_id,
            'team_id': self.team_id,
            'season_id': self.season_id,
            'shirt_number': self.shirt_number
        }
        
        if include_related:
            if self.player:
                result['player'] = self.player.to_dict()
            if self.team:
                result['team'] = self.team.to_dict()
            if self.season:
                result['season'] = self.season.to_dict()
        
        return result