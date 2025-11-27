from extensions import db

class Team(db.Model):
    """Mô hình Đội"""
    __tablename__ = 'Teams'
    team_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    logo_url = db.Column(db.String(255))
    home_stadium_id = db.Column(db.Integer, db.ForeignKey('Stadiums.stadium_id', ondelete='SET NULL'))

    # Relationships (Matches defined in Match model due to double FK)
    rosters = db.relationship('TeamRoster', backref='team', lazy=True)

    def __repr__(self):
        return f"<Team {self.name}>"

    def to_dict(self):
        return {
            'team_id': self.team_id,
            'name': self.name,
            'logo_url': self.logo_url,
            'home_stadium_id': self.home_stadium_id
        }
