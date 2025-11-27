from extensions import db

class Match(db.Model):
    """Mô hình Trận đấu"""
    __tablename__ = 'Matches'
    match_id = db.Column(db.Integer, primary_key=True)
    season_id = db.Column(db.Integer, db.ForeignKey('Seasons.season_id'), nullable=False)
    round = db.Column(db.String(50))
    match_datetime = db.Column(db.DateTime)
    home_team_id = db.Column(db.Integer, db.ForeignKey('Teams.team_id'), nullable=False)
    away_team_id = db.Column(db.Integer, db.ForeignKey('Teams.team_id'), nullable=False)
    home_score = db.Column(db.Integer)
    away_score = db.Column(db.Integer)
    status = db.Column(db.String(50))
    stadium_id = db.Column(db.Integer, db.ForeignKey('Stadiums.stadium_id'), nullable=False)
    match_url = db.Column(db.Text)

    # Relationships
    home_team = db.relationship('Team', foreign_keys=[home_team_id], backref='home_matches')
    away_team = db.relationship('Team', foreign_keys=[away_team_id], backref='away_matches')

    events = db.relationship('MatchEvent', backref='match', lazy=True)
    lineups = db.relationship('MatchLineup', backref='match', lazy=True)
    referees = db.relationship('MatchReferee', backref='match', lazy=True)

    def __repr__(self):
        return f"<Match {self.match_id}: {self.home_team_id} vs {self.away_team_id}>"

    def to_dict(self):
        return {
            'match_id': self.match_id,
            'season_id': self.season_id,
            'round': self.round,
            'match_datetime': self.match_datetime.isoformat() if self.match_datetime else None,
            'home_team_id': self.home_team_id,
            'away_team_id': self.away_team_id,
            'home_score': self.home_score,
            'away_score': self.away_score,
            'status': self.status,
            'stadium_id': self.stadium_id,
            'match_url': self.match_url
        }
