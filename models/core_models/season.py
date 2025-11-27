from extensions import db

class Season(db.Model):
    """Mô hình Mùa giải"""
    __tablename__ = 'Seasons'
    season_id = db.Column(db.Integer, primary_key=True)
    league_id = db.Column(db.Integer, db.ForeignKey('Leagues.league_id'))
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    vpf_sid = db.Column(db.Integer, unique=True, nullable=False)

    # Relationships
    matches = db.relationship('Match', backref='season', lazy=True)
    standings = db.relationship('SeasonStanding', backref='season', lazy=True)
    rosters = db.relationship('TeamRoster', backref='season', lazy=True)

    def __repr__(self):
        return f"<Season {self.name}>"

    def to_dict(self):
        return {
            'season_id': self.season_id,
            'league_id': self.league_id,
            'name': self.name,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'vpf_sid': self.vpf_sid
        }