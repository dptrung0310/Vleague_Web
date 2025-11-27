from flask import request
from flask_restx import Resource
from flask_jwt_extended import jwt_required
from extensions import cache
from services.team_player_services.player_service import PlayerService


def init_player_routes(api, namespace, schemas):
    player_service = PlayerService()

    output_model = schemas['player_output']
    input_model = schemas['player_input']

    @namespace.route('')
    class PlayerList(Resource):
        @namespace.doc('list_players')
        @namespace.marshal_list_with(output_model)
        @cache.cached(timeout=60, key_prefix='all_players')
        def get(self):
            """Lấy danh sách tất cả cầu thủ"""
            return player_service.get_all_players()

        @namespace.doc('create_player', security='jwt')
        @namespace.expect(input_model, validate=True)
        @jwt_required()
        def post(self):
            """Tạo hồ sơ cầu thủ mới"""
            cache.delete('all_players')
            return player_service.create_player(request.json)

    @namespace.route('/<int:id>')
    @namespace.param('id', 'Player ID')
    class PlayerResource(Resource):
        @namespace.doc('get_player')
        @namespace.marshal_with(output_model)
        @cache.cached(timeout=300)
        def get(self, id):
            """Lấy thông tin chi tiết cầu thủ"""
            return player_service.get_player_by_id(id)

        @namespace.doc('update_player', security='jwt')
        @namespace.expect(input_model)
        @jwt_required()
        def put(self, id):
            """Cập nhật thông tin cầu thủ"""
            cache.delete('all_players')
            return player_service.update_player(id, request.json)

        @namespace.doc('delete_player', security='jwt')
        @jwt_required()
        def delete(self, id):
            """Xóa hồ sơ cầu thủ"""
            cache.delete('all_players')
            return player_service.delete_player(id)