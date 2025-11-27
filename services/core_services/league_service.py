from models.core_models.league import League
from services.base import BaseService # Import BaseService

class LeagueService(BaseService):
    def get_all_leagues(self):
        leagues = League.query.all()
        return [l.to_dict() for l in leagues], 200

    def get_league_by_id(self, league_id):
        league = League.query.get(league_id)
        if not league:
            return {'message': 'Không tìm thấy giải đấu.'}, 404
        return league.to_dict(), 200

    def create_league(self, data):
        if data.get('code') and League.query.filter_by(code=data['code']).first():
            return {'message': 'Mã giải đấu đã tồn tại.'}, 409

        new_league = League(
            name=data['name'],
            code=data.get('code'),
            logo_url=data.get('logo_url')
        )

        # Sử dụng hàm save từ BaseService
        success, result = self.save(new_league)
        if success:
            return {'message': 'Tạo giải đấu thành công', 'league': result.to_dict()}, 201
        return {'message': f'Lỗi DB: {result}'}, 500

    def update_league(self, league_id, data):
        league = League.query.get(league_id)
        if not league:
            return {'message': 'Không tìm thấy giải đấu.'}, 404

        league.name = data.get('name', league.name)
        league.code = data.get('code', league.code)
        league.logo_url = data.get('logo_url', league.logo_url)

        success, result = self.save(league)
        if success:
            return {'message': 'Cập nhật thành công', 'league': result.to_dict()}, 200
        return {'message': f'Lỗi cập nhật: {result}'}, 500

    def delete_league(self, league_id):
        league = League.query.get(league_id)
        if not league:
            return {'message': 'Không tìm thấy giải đấu.'}, 404

        # Sử dụng hàm delete từ BaseService
        success, result = self.delete(league)
        if success:
            return {'message': 'Xóa giải đấu thành công.'}, 200
        return {'message': f'Lỗi xóa: {result}'}, 500