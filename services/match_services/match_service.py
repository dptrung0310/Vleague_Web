from models.match_models.match import Match
from services.base import BaseService
from datetime import datetime

class MatchService(BaseService):
    def get_all_matches(self):
        matches = Match.query.all()
        return [m.to_dict() for m in matches], 200

    def get_match_by_id(self, match_id):
        match = Match.query.get(match_id)
        if not match:
            return {'message': 'Không tìm thấy trận đấu.'}, 404
        return match.to_dict(), 200

    def _parse_datetime(self, dt_str):
        """Helper để parse datetime format YYYY-MM-DD HH:MM:SS"""
        if not dt_str: return None
        try:
            # Điều chỉnh format string tùy theo dữ liệu frontend gửi lên
            # Ví dụ: '2023-10-25 18:00:00'
            return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return None

    def create_match(self, data):
        new_match = Match(
            season_id=data['season_id'],
            round=data.get('round'),
            match_datetime=self._parse_datetime(data.get('match_datetime')),
            home_team_id=data['home_team_id'],
            away_team_id=data['away_team_id'],
            home_score=data.get('home_score'),
            away_score=data.get('away_score'),
            status=data.get('status', 'Scheduled'),
            stadium_id=data['stadium_id'],
            match_url=data.get('match_url')
        )

        success, result = self.save(new_match)
        if success:
            return {'message': 'Tạo trận đấu thành công', 'match': result.to_dict()}, 201
        return {'message': f'Lỗi DB: {result}'}, 500

    def update_match(self, match_id, data):
        match = Match.query.get(match_id)
        if not match:
            return {'message': 'Không tìm thấy trận đấu.'}, 404

        match.season_id = data.get('season_id', match.season_id)
        match.round = data.get('round', match.round)
        match.home_team_id = data.get('home_team_id', match.home_team_id)
        match.away_team_id = data.get('away_team_id', match.away_team_id)
        match.home_score = data.get('home_score', match.home_score)
        match.away_score = data.get('away_score', match.away_score)
        match.status = data.get('status', match.status)
        match.stadium_id = data.get('stadium_id', match.stadium_id)
        match.match_url = data.get('match_url', match.match_url)

        if 'match_datetime' in data:
            match.match_datetime = self._parse_datetime(data['match_datetime'])

        success, result = self.save(match)
        if success:
            return {'message': 'Cập nhật thành công', 'match': result.to_dict()}, 200
        return {'message': f'Lỗi cập nhật: {result}'}, 500

    def delete_match(self, match_id):
        match = Match.query.get(match_id)
        if not match:
            return {'message': 'Không tìm thấy trận đấu.'}, 404

        success, result = self.delete(match)
        if success:
            return {'message': 'Xóa trận đấu thành công.'}, 200
        return {'message': f'Lỗi xóa: {result}'}, 500