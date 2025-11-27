from extensions import db

class Stadium(db.Model):
    """Mô hình Sân vận động"""
    __tablename__ = 'Stadiums'
    stadium_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255))
    latitude = db.Column(db.Float) # DECIMAL(10, 7)
    longitude = db.Column(db.Float)

    # Relationships
    matches = db.relationship('Match', backref='stadium', lazy=True)
    teams = db.relationship('Team', backref='home_stadium', lazy=True)

    def __repr__(self):
        return f"<Stadium {self.name}>"

    def to_dict(self):
        return {
            'stadium_id': self.stadium_id,
            'name': self.name,
            'city': self.city,
            'address': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude
        }