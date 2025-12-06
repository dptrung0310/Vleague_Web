from extensions import db

class Stadium(db.Model):
    __tablename__ = 'Stadiums'
    
    stadium_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255))
    latitude = db.Column(db.Numeric(10, 7))
    longitude = db.Column(db.Numeric(10, 7))
    
    def to_dict(self):
        return {
            'stadium_id': self.stadium_id,
            'name': self.name,
            'city': self.city,
            'address': self.address,
            'latitude': float(self.latitude) if self.latitude else None,
            'longitude': float(self.longitude) if self.longitude else None
        }