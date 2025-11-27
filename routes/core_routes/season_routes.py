from flask import request
from flask_restx import Resource
from flask_jwt_extended import jwt_required
from extensions import cache
from services.core_services.season_service import SeasonService


def init_season_routes(api, namespace, schemas):
    """Khởi tạo các route cho Mùa giải (Season)"""
    season_service = SeasonService()

    season_output_model = schemas['season_output']
    season_input_model = schemas['season_input']

    @namespace.route('')
    class SeasonList(Resource):
        @namespace.doc(
            description='Lấy danh sách tất cả mùa giải',
            responses={200: 'Thành công'}
        )
        @namespace.marshal_list_with(season_output_model)
        @cache.cached(timeout=60, key_prefix='all_seasons')
        def get(self):
            """Lấy danh sách mùa giải (Read All)"""
            return season_service.get_all_seasons()

        @namespace.doc(
            security='jwt',
            description='Tạo mùa giải mới',
            responses={
                201: 'Tạo thành công',
                409: 'VPF SID đã tồn tại',
                401: 'Chưa xác thực'
            }
        )
        @namespace.expect(season_input_model, validate=True)
        @jwt_required()
        def post(self):
            """Tạo mùa giải mới (Create)"""
            cache.delete('all_seasons')
            data = request.json
            return season_service.create_season(data)

    @namespace.route('/<int:id>')
    @namespace.param('id', 'ID của mùa giải')
    class SeasonResource(Resource):
        @namespace.doc(
            description='Lấy thông tin chi tiết mùa giải',
            responses={
                200: 'Thành công',
                404: 'Không tìm thấy mùa giải'
            }
        )
        @namespace.marshal_with(season_output_model)
        @cache.cached(timeout=300)
        def get(self, id):
            """Lấy chi tiết mùa giải (Read One)"""
            return season_service.get_season_by_id(id)

        @namespace.doc(
            security='jwt',
            description='Cập nhật thông tin mùa giải',
            responses={200: 'Cập nhật thành công', 404: 'Not Found'}
        )
        @namespace.expect(season_input_model)
        @jwt_required()
        def put(self, id):
            """Cập nhật mùa giải (Update)"""
            cache.delete('all_seasons')
            data = request.json
            return season_service.update_season(id, data)

        @namespace.doc(
            security='jwt',
            description='Xóa mùa giải',
            responses={200: 'Xóa thành công', 404: 'Not Found'}
        )
        @jwt_required()
        def delete(self, id):
            """Xóa mùa giải (Delete)"""
            cache.delete('all_seasons')
            return season_service.delete_season(id)