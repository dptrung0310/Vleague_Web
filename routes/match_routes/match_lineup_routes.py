from flask import request
from flask_restx import Resource
from flask_jwt_extended import jwt_required
from extensions import cache
from services.match_services.match_lineup_service import MatchLineupService


def init_match_lineup_routes(api, namespace, schemas):
    lineup_service = MatchLineupService()

    lineup_output = schemas['lineup_output']
    lineup_input = schemas['lineup_input']

    @namespace.route('/match/<int:match_id>')
    class LineupByMatch(Resource):
        @namespace.doc('get_lineup_by_match')
        @namespace.marshal_list_with(lineup_output)
        def get(self, match_id):
            """Lấy danh sách đội hình của một trận đấu"""
            return lineup_service.get_lineup_by_match(match_id)

    @namespace.route('')
    class LineupCreate(Resource):
        @namespace.doc('create_lineup_entry', security='jwt')
        @namespace.expect(lineup_input, validate=True)
        @jwt_required()
        def post(self):
            """Thêm cầu thủ vào đội hình thi đấu"""
            # Nên clear cache của match lineups nếu có
            return lineup_service.create_lineup_entry(request.json)

    @namespace.route('/<int:id>')
    @namespace.param('id', 'Lineup Entry ID')
    class LineupResource(Resource):
        @namespace.doc('update_lineup_entry', security='jwt')
        @namespace.expect(lineup_input)
        @jwt_required()
        def put(self, id):
            """Cập nhật thông tin cầu thủ trong đội hình (Vị trí, Số áo...)"""
            return lineup_service.update_lineup_entry(id, request.json)

        @namespace.doc('delete_lineup_entry', security='jwt')
        @jwt_required()
        def delete(self, id):
            """Xóa cầu thủ khỏi đội hình"""
            return lineup_service.delete_lineup_entry(id)