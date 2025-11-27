from models.match_models.match_referee import MatchReferee
from services.base import BaseService

class MatchRefereeService(BaseService):
    def get_referees_by_match(self, match_id):
        refs = MatchReferee.query.filter_by(match_id=match_id).all()
        return [r.to_dict() for r in refs], 200

    def assign_referee(self, data):
        new_assignment = MatchReferee(
            match_id=data['match_id'],
            referee_id=data['referee_id'],
            role=data['role']
        )

        success, result = self.save(new_assignment)
        if success:
            return {'message': 'Phân công trọng tài thành công', 'assignment': result.to_dict()}, 201
        return {'message': f'Lỗi DB: {result}'}, 500

    def remove_referee_assignment(self, match_referee_id):
        assignment = MatchReferee.query.get(match_referee_id)
        if not assignment:
            return {'message': 'Không tìm thấy phân công này.'}, 404

        success, result = self.delete(assignment)
        if success:
            return {'message': 'Xóa phân công thành công'}, 200
        return {'message': f'Lỗi xóa: {result}'}, 500