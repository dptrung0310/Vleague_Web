from extensions import db

class Referee(db.Model):
    __tablename__ = 'Referees'
    
    referee_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False, unique=True)
    
    def to_dict(self):
        return {
            'referee_id': self.referee_id,
            'full_name': self.full_name
        }