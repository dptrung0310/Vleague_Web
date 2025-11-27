from extensions import db

class League(db.Model):
    __tablename__ = 'Leagues'
    league_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False) # Ví dụ: "V.League 1", "Cúp Quốc Gia"
    code = db.Column(db.String(20), unique=True)     # Ví dụ: "VL1", "VNC"
    logo_url = db.Column(db.String(255))

    # Mối quan hệ: Một giải đấu có nhiều mùa giải
    seasons = db.relationship('Season', backref='league', lazy=True)

    def to_dict(self):
        return {
            'league_id': self.league_id,
            'name': self.name,
            'code': self.code,
            'logo_url': self.logo_url
        }