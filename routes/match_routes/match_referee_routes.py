from flask import request
from flask_restx import Resource
from flask_jwt_extended import jwt_required
from extensions import cache
from services.match_services.match_referee_service import MatchRefereeService


def init_match_referee_routes(api, namespace, schemas):
    service = MatchRefereeService()

    output_model = schemas['match_referee_output']
    input_model = schemas['match_referee_input']

    @namespace.route('/match/<int:match_id>')
    class RefereeByMatch(Resource):
        @namespace.doc('get_referees_by_match')
        @namespace.marshal_list_with(output_model)
        def get(self, match_id):
            """Lấy danh sách trọng tài làm nhiệm vụ tại trận đấu"""
            return service.get_referees_by_match(match_id)

    @namespace.route('')
    class AssignReferee(Resource):
        @namespace.doc('assign_referee', security='jwt')
        @namespace.expect(input_model, validate=True)
        @jwt_required()
        def post(self):
            """Phân công trọng tài cho trận đấu"""
            return service.assign_referee(request.json)

    @namespace.route('/<int:id>')
    @namespace.param('id', 'Match Referee Assignment ID')
    class RefereeAssignmentResource(Resource):
        @namespace.doc('remove_referee_assignment', security='jwt')
        @jwt_required()
        def delete(self, id):
            """Xóa phân công trọng tài"""
            return service.remove_referee_assignment(id)