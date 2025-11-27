from models.standing_model.season_standing import SeasonStanding
from services.base import BaseService

class SeasonStandingService(BaseService):
    def get_standings(self, season_id, round_num=None):
        """
        Lấy bảng xếp hạng.
        Nếu có round_num -> lấy của vòng đó.
        Nếu không -> lấy tất cả (hoặc bạn có thể logic lấy vòng mới nhất).
        """
        query = SeasonStanding.query.filter_by(season_id=season_id)

        if round_num is not None:
            query = query.filter_by(round=round_num)

        # Sắp xếp theo chuẩn bóng đá: Điểm > Hiệu số > Bàn thắng > Tên đội (hoặc vị trí)
        # Lưu ý: Cần import desc từ sqlalchemy nếu muốn dùng .desc() trong order_by
        # Tuy nhiên query.order_by(Model.field.desc()) là cú pháp chuẩn của SQLAlchemy ORM
        standings = query.order_by(
            SeasonStanding.points.desc(),
            SeasonStanding.goal_difference.desc(),
            SeasonStanding.goals_for.desc()
        ).all()

        return [s.to_dict() for s in standings], 200

    def _calculate_metrics(self, data):
        """Hàm phụ trợ: Tự động tính toán các chỉ số derived"""
        wins = int(data.get('wins', 0))
        draws = int(data.get('draws', 0))
        losses = int(data.get('losses', 0))
        gf = int(data.get('goals_for', 0))
        ga = int(data.get('goals_against', 0))

        # Tự tính số trận đã đấu
        played = wins + draws + losses
        # Tự tính điểm (Thắng 3, Hòa 1)
        points = (wins * 3) + (draws * 1)
        # Tự tính hiệu số
        goal_diff = gf - ga

        return played, points, goal_diff

    def create_standing_entry(self, data):
        """Tạo mới một dòng xếp hạng cho 1 đội tại 1 vòng"""
        # Kiểm tra trùng lặp (1 đội không thể có 2 dòng xếp hạng trong cùng 1 vòng)
        if SeasonStanding.query.filter_by(
                season_id=data['season_id'],
                team_id=data['team_id'],
                round=data['round']
        ).first():
            return {'message': 'Dữ liệu xếp hạng cho đội này tại vòng này đã tồn tại.'}, 409

        # Tự động tính toán để đảm bảo dữ liệu đúng
        played, points, goal_diff = self._calculate_metrics(data)

        new_standing = SeasonStanding(
            season_id=data['season_id'],
            team_id=data['team_id'],
            round=data['round'],
            position=data.get('position', 0),  # Vị trí tạm thời, có thể update sau khi sort
            played=played,
            wins=data['wins'],
            draws=data['draws'],
            losses=data['losses'],
            goals_for=data['goals_for'],
            goals_against=data['goals_against'],
            goal_difference=goal_diff,
            points=points
        )

        success, result = self.save(new_standing)
        if success:
            return {'message': 'Thêm xếp hạng thành công', 'standing': result.to_dict()}, 201
        return {'message': f'Lỗi DB: {result}'}, 500

    def update_standing_entry(self, standing_id, data):
        standing = SeasonStanding.query.get(standing_id)
        if not standing:
            return {'message': 'Không tìm thấy dữ liệu.'}, 404

        # Cập nhật các chỉ số cơ bản
        standing.wins = data.get('wins', standing.wins)
        standing.draws = data.get('draws', standing.draws)
        standing.losses = data.get('losses', standing.losses)
        standing.goals_for = data.get('goals_for', standing.goals_for)
        standing.goals_against = data.get('goals_against', standing.goals_against)
        standing.position = data.get('position', standing.position)

        # Recalculate các chỉ số phụ dựa trên dữ liệu mới nhất trong object
        # (Lưu ý: cần convert về dict hoặc truyền tham số lẻ để dùng hàm _calculate_metrics,
        # ở đây tôi viết inline cho đơn giản vì object đã update giá trị mới)
        standing.played = standing.wins + standing.draws + standing.losses
        standing.points = (standing.wins * 3) + (standing.draws * 1)
        standing.goal_difference = standing.goals_for - standing.goals_against

        success, result = self.save(standing)
        if success:
            return {'message': 'Cập nhật thành công', 'standing': result.to_dict()}, 200
        return {'message': f'Lỗi cập nhật: {result}'}, 500

    def delete_standing_entry(self, standing_id):
        standing = SeasonStanding.query.get(standing_id)
        if not standing:
            return {'message': 'Không tìm thấy dữ liệu.'}, 404

        success, result = self.delete(standing)
        if success:
            return {'message': 'Xóa thành công.'}, 200
        return {'message': f'Lỗi xóa: {result}'}, 500