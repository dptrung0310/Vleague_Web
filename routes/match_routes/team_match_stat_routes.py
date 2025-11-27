from flask import request
from flask_restx import Resource
from flask_jwt_extended import jwt_required
from extensions import cache
from services.match_services.team_match_stat_service import TeamMatchStatService


def init_team_match_stat_routes(api, namespace, schemas):
    service = TeamMatchStatService()

    output_model = schemas['stat_output']
    input_model = schemas['stat_input']

    @namespace.route('/match/<int:match_id>')
    class StatsByMatch(Resource):
        @namespace.doc('get_stats_by_match')
        @namespace.marshal_list_with(output_model)
        def get(self, match_id):
            """Lấy thống kê chi tiết của trận đấu"""
            return service.get_stats_by_match(match_id)

    @namespace.route('')
    class CreateUpdateStat(Resource):
        @namespace.doc('create_or_update_stat', security='jwt')
        @namespace.expect(input_model, validate=True)
        @jwt_required()
        def post(self):
            """Tạo hoặc Cập nhật thống kê cho đội bóng trong trận đấu"""
            # Service này dùng logic create_or_update nên dùng chung 1 endpoint POST
            return service.create_or_update_stat(request.json)