from extensions import db
from datetime import date

class Season(db.Model):
    __tablename__ = 'Seasons'
    
    season_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    vpf_sid = db.Column(db.Integer, nullable=False, unique=True)
    
    def to_dict(self):
        return {
            'season_id': self.season_id,
            'name': self.name,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'vpf_sid': self.vpf_sid
        }