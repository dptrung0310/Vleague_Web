from models.match_models.team_match_stat import TeamMatchStat
from services.base import BaseService


class TeamMatchStatService(BaseService):
    def get_stats_by_match(self, match_id):
        stats = TeamMatchStat.query.filter_by(match_id=match_id).all()
        return [s.to_dict() for s in stats], 200

    def create_or_update_stat(self, data):
        # Kiểm tra xem đã có thống kê cho đội này trong trận này chưa
        stat = TeamMatchStat.query.filter_by(match_id=data['match_id'], team_id=data['team_id']).first()

        if not stat:
            stat = TeamMatchStat(
                match_id=data['match_id'],
                team_id=data['team_id']
            )
            # Thêm mới session add sẽ được gọi trong self.save nếu đối tượng chưa attach

        # Cập nhật các chỉ số
        stat.possession_percentage = data.get('possession_percentage', stat.possession_percentage)
        stat.shots_on_target = data.get('shots_on_target', stat.shots_on_target)
        stat.shots_off_target = data.get('shots_off_target', stat.shots_off_target)
        stat.corners = data.get('corners', stat.corners)
        stat.offsides = data.get('offsides', stat.offsides)
        stat.fouls = data.get('fouls', stat.fouls)
        stat.yellow_cards = data.get('yellow_cards', stat.yellow_cards)
        stat.red_cards = data.get('red_cards', stat.red_cards)

        success, result = self.save(stat)
        if success:
            return {'message': 'Lưu thống kê thành công', 'stat': result.to_dict()}, 200  # Hoặc 201 nếu tạo mới
        return {'message': f'Lỗi DB: {result}'}, 500