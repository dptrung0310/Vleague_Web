from models.core_models.referee import Referee
from services.base import BaseService


class RefereeService(BaseService):
    def get_all_referees(self):
        referees = Referee.query.all()
        return [r.to_dict() for r in referees], 200

    def get_referee_by_id(self, referee_id):
        referee = Referee.query.get(referee_id)
        if not referee:
            return {'message': 'Không tìm thấy trọng tài.'}, 404
        return referee.to_dict(), 200

    def create_referee(self, data):
        if Referee.query.filter_by(full_name=data['full_name']).first():
            return {'message': 'Tên trọng tài đã tồn tại.'}, 409

        new_referee = Referee(full_name=data['full_name'])

        success, result = self.save(new_referee)
        if success:
            return {'message': 'Thêm trọng tài thành công', 'referee': result.to_dict()}, 201
        return {'message': f'Lỗi DB: {result}'}, 500

    def update_referee(self, referee_id, data):
        referee = Referee.query.get(referee_id)
        if not referee:
            return {'message': 'Không tìm thấy trọng tài.'}, 404

        referee.full_name = data.get('full_name', referee.full_name)

        success, result = self.save(referee)
        if success:
            return {'message': 'Cập nhật thành công', 'referee': result.to_dict()}, 200
        return {'message': f'Lỗi cập nhật: {result}'}, 500

    def delete_referee(self, referee_id):
        referee = Referee.query.get(referee_id)
        if not referee:
            return {'message': 'Không tìm thấy trọng tài.'}, 404

        success, result = self.delete(referee)
        if success:
            return {'message': 'Xóa trọng tài thành công.'}, 200
        return {'message': f'Lỗi xóa: {result}'}, 500