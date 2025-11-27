from models.match_models.match_lineup import MatchLineup
from services.base import BaseService


class MatchLineupService(BaseService):
    def get_lineup_by_match(self, match_id):
        lineups = MatchLineup.query.filter_by(match_id=match_id).all()
        return [l.to_dict() for l in lineups], 200

    def create_lineup_entry(self, data):
        # Kiểm tra logic nếu cần (ví dụ: đã tồn tại cầu thủ trong trận đấu chưa)
        # Tuy nhiên DB đã có UniqueConstraint('match_id', 'player_id') nên sẽ bắn lỗi nếu trùng

        new_entry = MatchLineup(
            match_id=data['match_id'],
            team_id=data['team_id'],
            player_id=data['player_id'],
            is_starter=data.get('is_starter', False),
            shirt_number=data['shirt_number'],
            position=data.get('position')
        )

        success, result = self.save(new_entry)
        if success:
            return {'message': 'Thêm cầu thủ vào đội hình thành công', 'lineup': result.to_dict()}, 201
        return {'message': f'Lỗi DB: {result}'}, 500

    def update_lineup_entry(self, lineup_id, data):
        entry = MatchLineup.query.get(lineup_id)
        if not entry:
            return {'message': 'Không tìm thấy.'}, 404

        entry.is_starter = data.get('is_starter', entry.is_starter)
        entry.shirt_number = data.get('shirt_number', entry.shirt_number)
        entry.position = data.get('position', entry.position)

        success, result = self.save(entry)
        if success:
            return {'message': 'Cập nhật thành công', 'lineup': result.to_dict()}, 200
        return {'message': f'Lỗi cập nhật: {result}'}, 500

    def delete_lineup_entry(self, lineup_id):
        entry = MatchLineup.query.get(lineup_id)
        if not entry:
            return {'message': 'Không tìm thấy.'}, 404

        success, result = self.delete(entry)
        if success:
            return {'message': 'Xóa thành công'}, 200
        return {'message': f'Lỗi xóa: {result}'}, 500