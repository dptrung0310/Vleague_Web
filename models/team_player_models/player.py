from sqlalchemy import UniqueConstraint

from extensions import db

class Player(db.Model):
    """Mô hình Thông tin người chơi"""
    __tablename__ = 'Players'
    player_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date)
    height_cm = db.Column(db.Integer)
    weight_kg = db.Column(db.Integer)
    position = db.Column(db.String(50))
    image_url = db.Column(db.String(255))

    __table_args__ = (UniqueConstraint('full_name', 'birth_date', name='uk_name_dob'),)

    # Relationships
    rosters = db.relationship('TeamRoster', backref='player', lazy=True)

    def __repr__(self):
        return f"<Player {self.full_name}>"

    def to_dict(self):
        return {
            'player_id': self.player_id,
            'full_name': self.full_name,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'height_cm': self.height_cm,
            'weight_kg': self.weight_kg,
            'position': self.position,
            'image_url': self.image_url
        }
