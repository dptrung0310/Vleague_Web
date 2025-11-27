from flask import request
from flask_restx import Resource
from flask_jwt_extended import jwt_required
from extensions import cache
from services.team_player_services.team_service import TeamService


def init_team_routes(api, namespace, schemas):
    team_service = TeamService()

    output_model = schemas['team_output']
    input_model = schemas['team_input']

    @namespace.route('')
    class TeamList(Resource):
        @namespace.doc('list_teams')
        @namespace.marshal_list_with(output_model)
        @cache.cached(timeout=60, key_prefix='all_teams')
        def get(self):
            """Lấy danh sách tất cả các đội bóng"""
            return team_service.get_all_teams()

        @namespace.doc('create_team', security='jwt')
        @namespace.expect(input_model, validate=True)
        @jwt_required()
        def post(self):
            """Tạo đội bóng mới"""
            cache.delete('all_teams')
            return team_service.create_team(request.json)

    @namespace.route('/<int:id>')
    @namespace.param('id', 'Team ID')
    class TeamResource(Resource):
        @namespace.doc('get_team')
        @namespace.marshal_with(output_model)
        @cache.cached(timeout=300)
        def get(self, id):
            """Lấy thông tin chi tiết đội bóng"""
            return team_service.get_team_by_id(id)

        @namespace.doc('update_team', security='jwt')
        @namespace.expect(input_model)
        @jwt_required()
        def put(self, id):
            """Cập nhật thông tin đội bóng"""
            cache.delete('all_teams')
            # Xóa cache detail nếu có thể: cache.delete_memoized(self.get, id)
            return team_service.update_team(id, request.json)

        @namespace.doc('delete_team', security='jwt')
        @jwt_required()
        def delete(self, id):
            """Xóa đội bóng"""
            cache.delete('all_teams')
            return team_service.delete_team(id)