from extensions import db

class Referee(db.Model):
    """Mô hình trọng tài"""
    __tablename__ = 'Referees'
    referee_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String, unique=True, nullable=False)

    def __repr__(self):
        return f"<Referee {self.full_name}>"

    def to_dict(self):
        return {
            'referee_id': self.referee_id,
            'full_name': self.full_name
        }