from models.core_models.season import Season
from services.base import BaseService
from datetime import datetime


class SeasonService(BaseService):
    def get_all_seasons(self):
        seasons = Season.query.all()
        return [s.to_dict() for s in seasons], 200

    def get_season_by_id(self, season_id):
        season = Season.query.get(season_id)
        if not season:
            return {'message': 'Không tìm thấy mùa giải.'}, 404
        return season.to_dict(), 200

    def _parse_date(self, date_str):
        """Helper nội bộ để parse ngày tháng"""
        if not date_str: return None
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return None

    def create_season(self, data):
        if Season.query.filter_by(vpf_sid=data['vpf_sid']).first():
            return {'message': 'VPF SID đã tồn tại.'}, 409

        new_season = Season(
            league_id=data['league_id'],
            name=data['name'],
            vpf_sid=data['vpf_sid'],
            start_date=self._parse_date(data.get('start_date')),
            end_date=self._parse_date(data.get('end_date'))
        )

        success, result = self.save(new_season)
        if success:
            return {'message': 'Tạo mùa giải thành công', 'season': result.to_dict()}, 201
        return {'message': f'Lỗi DB: {result}'}, 500

    def update_season(self, season_id, data):
        season = Season.query.get(season_id)
        if not season:
            return {'message': 'Không tìm thấy mùa giải.'}, 404

        season.league_id = data.get('league_id', season.league_id)
        season.name = data.get('name', season.name)
        season.vpf_sid = data.get('vpf_sid', season.vpf_sid)

        if 'start_date' in data:
            season.start_date = self._parse_date(data['start_date'])
        if 'end_date' in data:
            season.end_date = self._parse_date(data['end_date'])

        success, result = self.save(season)
        if success:
            return {'message': 'Cập nhật thành công', 'season': result.to_dict()}, 200
        return {'message': f'Lỗi cập nhật: {result}'}, 500

    def delete_season(self, season_id):
        season = Season.query.get(season_id)
        if not season:
            return {'message': 'Không tìm thấy mùa giải.'}, 404

        success, result = self.delete(season)
        if success:
            return {'message': 'Xóa mùa giải thành công.'}, 200
        return {'message': f'Lỗi xóa: {result}'}, 500