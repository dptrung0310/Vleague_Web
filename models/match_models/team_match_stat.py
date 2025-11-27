from extensions import db

class TeamMatchStat(db.Model):
    """Mô hình Thống kê chi tiết trận đấu"""
    __tablename__ = 'TeamMatchStats'
    stat_id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('Matches.match_id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('Teams.team_id'), nullable=False)

    # Các chỉ số quan trọng cho phân tích
    possession_percentage = db.Column(db.Integer)  # Tỉ lệ kiểm soát bóng (%)
    shots_on_target = db.Column(db.Integer)  # Sút trúng đích
    shots_off_target = db.Column(db.Integer)  # Sút trượt
    corners = db.Column(db.Integer)  # Phạt góc
    offsides = db.Column(db.Integer)  # Việt vị
    fouls = db.Column(db.Integer)  # Phạm lỗi
    yellow_cards = db.Column(db.Integer)  # (Có thể tính từ MatchEvents nhưng lưu ở đây để query nhanh)
    red_cards = db.Column(db.Integer)

    # Mối quan hệ
    match = db.relationship('Match', backref='stats')
    team = db.relationship('Team')

    def to_dict(self):
        return {
            'stat_id': self.stat_id,
            'match_id': self.match_id,
            'team_id': self.team_id,
            'possession_percentage': self.possession_percentage,
            'shots_on_target': self.shots_on_target,
            'shots_off_target': self.shots_off_target,
            'corners': self.corners,
            'offsides': self.offsides,
            'fouls': self.fouls,
            'yellow_cards': self.yellow_cards,
            'red_cards': self.red_cards
        }