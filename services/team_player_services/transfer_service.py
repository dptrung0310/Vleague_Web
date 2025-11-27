from models.team_player_models.transfer import Transfer
from services.base import BaseService
from datetime import datetime

class TransferService(BaseService):
    def get_transfers_by_season(self, season_id):
        transfers = Transfer.query.filter_by(season_id=season_id).all()
        return [t.to_dict() for t in transfers], 200

    def _parse_date(self, date_str):
        if not date_str: return None
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return None

    def create_transfer(self, data):
        new_transfer = Transfer(
            player_id=data['player_id'],
            from_team_id=data.get('from_team_id'), # Có thể None
            to_team_id=data['to_team_id'],
            season_id=data.get('season_id'),
            transfer_date=self._parse_date(data.get('transfer_date')),
            transfer_type=data.get('transfer_type'),
            transfer_fee=data.get('transfer_fee')
        )

        success, result = self.save(new_transfer)
        if success:
            return {'message': 'Ghi nhận chuyển nhượng thành công', 'transfer': result.to_dict()}, 201
        return {'message': f'Lỗi DB: {result}'}, 500

    def delete_transfer(self, transfer_id):
        transfer = Transfer.query.get(transfer_id)
        if not transfer:
            return {'message': 'Không tìm thấy bản ghi chuyển nhượng.'}, 404

        success, result = self.delete(transfer)
        if success:
            return {'message': 'Xóa bản ghi thành công.'}, 200
        return {'message': f'Lỗi xóa: {result}'}, 500