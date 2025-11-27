from models.team_player_models.player import Player
from services.base import BaseService
from datetime import datetime


class PlayerService(BaseService):
    def get_all_players(self):
        players = Player.query.all()
        return [p.to_dict() for p in players], 200

    def get_player_by_id(self, player_id):
        player = Player.query.get(player_id)
        if not player:
            return {'message': 'Không tìm thấy cầu thủ.'}, 404
        return player.to_dict(), 200

    def _parse_date(self, date_str):
        if not date_str: return None
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return None

    def create_player(self, data):
        # Check unique constraint (full_name + birth_date)
        dob = self._parse_date(data.get('birth_date'))
        if Player.query.filter_by(full_name=data['full_name'], birth_date=dob).first():
            return {'message': 'Cầu thủ này đã tồn tại.'}, 409

        new_player = Player(
            full_name=data['full_name'],
            birth_date=dob,
            height_cm=data.get('height_cm'),
            weight_kg=data.get('weight_kg'),
            position=data.get('position'),
            image_url=data.get('image_url')
        )

        success, result = self.save(new_player)
        if success:
            return {'message': 'Thêm cầu thủ thành công', 'player': result.to_dict()}, 201
        return {'message': f'Lỗi DB: {result}'}, 500

    def update_player(self, player_id, data):
        player = Player.query.get(player_id)
        if not player:
            return {'message': 'Không tìm thấy cầu thủ.'}, 404

        player.full_name = data.get('full_name', player.full_name)
        if 'birth_date' in data:
            player.birth_date = self._parse_date(data['birth_date'])

        player.height_cm = data.get('height_cm', player.height_cm)
        player.weight_kg = data.get('weight_kg', player.weight_kg)
        player.position = data.get('position', player.position)
        player.image_url = data.get('image_url', player.image_url)

        success, result = self.save(player)
        if success:
            return {'message': 'Cập nhật thành công', 'player': result.to_dict()}, 200
        return {'message': f'Lỗi cập nhật: {result}'}, 500

    def delete_player(self, player_id):
        player = Player.query.get(player_id)
        if not player:
            return {'message': 'Không tìm thấy cầu thủ.'}, 404

        success, result = self.delete(player)
        if success:
            return {'message': 'Xóa cầu thủ thành công.'}, 200
        return {'message': f'Lỗi xóa: {result}'}, 500