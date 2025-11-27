from models.team_player_models.team import Team
from services.base import BaseService

class TeamService(BaseService):
    def get_all_teams(self):
        teams = Team.query.all()
        return [t.to_dict() for t in teams], 200

    def get_team_by_id(self, team_id):
        team = Team.query.get(team_id)
        if not team:
            return {'message': 'Không tìm thấy đội bóng.'}, 404
        return team.to_dict(), 200

    def create_team(self, data):
        if Team.query.filter_by(name=data['name']).first():
            return {'message': 'Tên đội bóng đã tồn tại.'}, 409

        new_team = Team(
            name=data['name'],
            logo_url=data.get('logo_url'),
            home_stadium_id=data.get('home_stadium_id')
        )

        success, result = self.save(new_team)
        if success:
            return {'message': 'Tạo đội bóng thành công', 'team': result.to_dict()}, 201
        return {'message': f'Lỗi DB: {result}'}, 500

    def update_team(self, team_id, data):
        team = Team.query.get(team_id)
        if not team:
            return {'message': 'Không tìm thấy đội bóng.'}, 404

        # Nếu đổi tên, cần check trùng
        if 'name' in data and data['name'] != team.name:
            if Team.query.filter_by(name=data['name']).first():
                return {'message': 'Tên đội bóng đã tồn tại.'}, 409
            team.name = data['name']

        team.logo_url = data.get('logo_url', team.logo_url)
        team.home_stadium_id = data.get('home_stadium_id', team.home_stadium_id)

        success, result = self.save(team)
        if success:
            return {'message': 'Cập nhật thành công', 'team': result.to_dict()}, 200
        return {'message': f'Lỗi cập nhật: {result}'}, 500

    def delete_team(self, team_id):
        team = Team.query.get(team_id)
        if not team:
            return {'message': 'Không tìm thấy đội bóng.'}, 404

        success, result = self.delete(team)
        if success:
            return {'message': 'Xóa đội bóng thành công.'}, 200
        return {'message': f'Lỗi xóa: {result}'}, 500