from flask import request
from flask_restx import Resource
from flask_jwt_extended import jwt_required
from extensions import cache
from services.match_services.match_service import MatchService


def init_match_routes(api, namespace, schemas):
    match_service = MatchService()

    match_output = schemas['match_output']
    match_input = schemas['match_input']

    @namespace.route('')
    class MatchList(Resource):
        @namespace.doc('list_matches')
        @namespace.marshal_list_with(match_output)
        @cache.cached(timeout=60, key_prefix='all_matches')
        def get(self):
            """Lấy danh sách tất cả trận đấu"""
            return match_service.get_all_matches()

        @namespace.doc('create_match', security='jwt')
        @namespace.expect(match_input, validate=True)
        @jwt_required()
        def post(self):
            """Tạo trận đấu mới"""
            cache.delete('all_matches')
            return match_service.create_match(request.json)

    @namespace.route('/<int:id>')
    @namespace.param('id', 'Match ID')
    class MatchResource(Resource):
        @namespace.doc('get_match')
        @namespace.marshal_with(match_output)
        @cache.cached(timeout=60)
        def get(self, id):
            """Chi tiết trận đấu"""
            return match_service.get_match_by_id(id)

        @namespace.doc('update_match', security='jwt')
        @namespace.expect(match_input)
        @jwt_required()
        def put(self, id):
            """Cập nhật thông tin trận đấu"""
            cache.delete('all_matches')
            cache.delete_memoized(self.get, id)
            return match_service.update_match(id, request.json)

        @namespace.doc('delete_match', security='jwt')
        @jwt_required()
        def delete(self, id):
            """Xóa trận đấu"""
            cache.delete('all_matches')
            return match_service.delete_match(id)