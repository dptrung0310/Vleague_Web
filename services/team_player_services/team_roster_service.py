from models.team_player_models.team_roster import TeamRoster
from services.base import BaseService


class TeamRosterService(BaseService):
    def get_roster_by_team_season(self, team_id, season_id):
        roster = TeamRoster.query.filter_by(team_id=team_id, season_id=season_id).all()
        return [r.to_dict() for r in roster], 200

    def add_player_to_roster(self, data):
        # DB Constraints sẽ lo việc check unique (player_id + season_id)
        # và (team_id + season_id + shirt_number)

        new_entry = TeamRoster(
            player_id=data['player_id'],
            team_id=data['team_id'],
            season_id=data['season_id'],
            shirt_number=data.get('shirt_number')
        )

        success, result = self.save(new_entry)
        if success:
            return {'message': 'Thêm cầu thủ vào đội hình thành công', 'roster': result.to_dict()}, 201

        # Xử lý thông báo lỗi cụ thể hơn nếu muốn
        if "uk_player_season" in str(result):
            return {'message': 'Cầu thủ đã đăng ký cho một đội khác trong mùa giải này.'}, 409
        if "uk_team_season_shirt" in str(result):
            return {'message': 'Số áo này đã có người sử dụng trong đội.'}, 409

        return {'message': f'Lỗi DB: {result}'}, 500

    def update_roster_entry(self, roster_id, data):
        entry = TeamRoster.query.get(roster_id)
        if not entry:
            return {'message': 'Không tìm thấy thông tin đăng ký.'}, 404

        entry.shirt_number = data.get('shirt_number', entry.shirt_number)
        # Thường ít khi đổi team_id hay player_id trực tiếp, nên xóa đi tạo lại tốt hơn
        # Nhưng nếu cần:
        if 'team_id' in data: entry.team_id = data['team_id']

        success, result = self.save(entry)
        if success:
            return {'message': 'Cập nhật thành công', 'roster': result.to_dict()}, 200
        return {'message': f'Lỗi cập nhật: {result}'}, 500

    def remove_from_roster(self, roster_id):
        entry = TeamRoster.query.get(roster_id)
        if not entry:
            return {'message': 'Không tìm thấy.'}, 404

        success, result = self.delete(entry)
        if success:
            return {'message': 'Xóa khỏi danh sách thi đấu thành công.'}, 200
        return {'message': f'Lỗi xóa: {result}'}, 500