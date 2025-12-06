# models/match.py - sửa lại với relationships
from extensions import db
from datetime import datetime

class Match(db.Model):
    __tablename__ = 'Matches'
    
    match_id = db.Column(db.Integer, primary_key=True)
    season_id = db.Column(db.Integer, db.ForeignKey('Seasons.season_id'), nullable=False)
    round = db.Column(db.String(50))
    match_datetime = db.Column(db.DateTime, nullable=False)
    home_team_id = db.Column(db.Integer, db.ForeignKey('Teams.team_id'), nullable=False)
    away_team_id = db.Column(db.Integer, db.ForeignKey('Teams.team_id'), nullable=False)
    home_score = db.Column(db.Integer)
    away_score = db.Column(db.Integer)
    status = db.Column(db.String(50))
    stadium_id = db.Column(db.Integer, db.ForeignKey('Stadiums.stadium_id'), nullable=False)
    match_url = db.Column(db.Text)
    
    # Relationships
    season = db.relationship('Season', backref='matches')
    home_team = db.relationship('Team', foreign_keys=[home_team_id], backref='home_matches')
    away_team = db.relationship('Team', foreign_keys=[away_team_id], backref='away_matches')
    stadium = db.relationship('Stadium', backref='matches')
    referees = db.relationship('MatchReferee', backref='match', cascade='all, delete-orphan')
    lineups = db.relationship('MatchLineup', backref='match', cascade='all, delete-orphan')
    events = db.relationship('MatchEvent', backref='match', cascade='all, delete-orphan')
    
    def to_dict(self, include_related=False):
        """Chuyển đổi object thành dictionary"""
        result = {
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
        
        if include_related:
            # Thêm thông tin liên quan
            if self.season:
                result['season'] = self.season.to_dict()
            if self.home_team:
                result['home_team'] = self.home_team.to_dict()
            if self.away_team:
                result['away_team'] = self.away_team.to_dict()
            if self.stadium:
                result['stadium'] = self.stadium.to_dict()
        
        return result