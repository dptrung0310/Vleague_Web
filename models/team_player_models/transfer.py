from extensions import db

class Transfer(db.Model):
    __tablename__ = 'Transfers'
    transfer_id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('Players.player_id'), nullable=False)
    from_team_id = db.Column(db.Integer, db.ForeignKey('Teams.team_id'))  # Có thể Null nếu cầu thủ tự do
    to_team_id = db.Column(db.Integer, db.ForeignKey('Teams.team_id'), nullable=False)
    season_id = db.Column(db.Integer, db.ForeignKey('Seasons.season_id'))

    transfer_date = db.Column(db.Date)
    transfer_type = db.Column(db.String(50))  # 'buy', 'loan', 'free'
    transfer_fee = db.Column(db.Float)  # Phí chuyển nhượng (nếu có)

    player = db.relationship('Player', backref='transfers')

    def to_dict(self):
        return {
            'transfer_id': self.transfer_id,
            'player_id': self.player_id,
            'from_team_id': self.from_team_id,
            'to_team_id': self.to_team_id,
            'season_id': self.season_id,
            'transfer_date': self.transfer_date.isoformat() if self.transfer_date else None,
            'transfer_type': self.transfer_type,
            'transfer_fee': self.transfer_fee
        }
