from flask import request
from flask_restx import Resource
from flask_jwt_extended import jwt_required
from extensions import cache
from services.team_player_services.team_roster_service import TeamRosterService


def init_team_roster_routes(api, namespace, schemas):
    roster_service = TeamRosterService()

    output_model = schemas['roster_output']
    input_model = schemas['roster_input']

    @namespace.route('/team/<int:team_id>/season/<int:season_id>')
    @namespace.param('team_id', 'ID Đội bóng')
    @namespace.param('season_id', 'ID Mùa giải')
    class RosterList(Resource):
        @namespace.doc('get_roster_by_team_season')
        @namespace.marshal_list_with(output_model)
        def get(self, team_id, season_id):
            """Lấy danh sách cầu thủ của đội trong một mùa giải"""
            return roster_service.get_roster_by_team_season(team_id, season_id)

    @namespace.route('')
    class RosterEntry(Resource):
        @namespace.doc('add_player_to_roster', security='jwt')
        @namespace.expect(input_model, validate=True)
        @jwt_required()
        def post(self):
            """Đăng ký cầu thủ vào đội bóng cho mùa giải"""
            return roster_service.add_player_to_roster(request.json)

    @namespace.route('/<int:id>')
    @namespace.param('id', 'Roster ID')
    class RosterResource(Resource):
        @namespace.doc('update_roster_entry', security='jwt')
        @namespace.expect(input_model)
        @jwt_required()
        def put(self, id):
            """Cập nhật thông tin đăng ký (ví dụ: đổi số áo)"""
            return roster_service.update_roster_entry(id, request.json)

        @namespace.doc('remove_from_roster', security='jwt')
        @jwt_required()
        def delete(self, id):
            """Xóa cầu thủ khỏi danh sách đăng ký"""
            return roster_service.remove_from_roster(id)