from extensions import db

class Team(db.Model):
    __tablename__ = 'Teams'
    
    team_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    logo_url = db.Column(db.String(255))
    home_stadium_id = db.Column(db.Integer, db.ForeignKey('Stadiums.stadium_id'))
    
    # Relationship
    home_stadium = db.relationship('Stadium', backref='teams')
    
    def to_dict(self, include_stadium=False):
        result = {
            'team_id': self.team_id,
            'name': self.name,
            'logo_url': self.logo_url,
            'home_stadium_id': self.home_stadium_id
        }
        
        if include_stadium and self.home_stadium:
            result['home_stadium'] = self.home_stadium.to_dict()
        
        return result