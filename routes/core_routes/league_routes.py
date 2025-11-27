from flask import request
from flask_restx import Resource
from flask_jwt_extended import jwt_required
from extensions import cache
from services.core_services.league_service import LeagueService


def init_league_routes(api, namespace, schemas):
    """Khởi tạo các route cho Giải đấu (League)"""
    league_service = LeagueService()

    # Lấy model từ schemas
    league_output_model = schemas['league_output']
    league_input_model = schemas['league_input']

    @namespace.route('')
    class LeagueList(Resource):
        @namespace.doc(
            description='Lấy danh sách tất cả các giải đấu',
            responses={
                200: 'Lấy dữ liệu thành công',
                500: 'Lỗi server nội bộ'
            }
        )
        @namespace.marshal_list_with(league_output_model)
        @cache.cached(timeout=60, key_prefix='all_leagues')  # Cache danh sách trong 60s
        def get(self):
            """Lấy danh sách giải đấu (Read All)"""
            return league_service.get_all_leagues()

        @namespace.doc(
            security='jwt',
            description='Tạo mới một giải đấu',
            responses={
                201: 'Tạo thành công',
                400: 'Dữ liệu không hợp lệ',
                409: 'Mã giải đấu đã tồn tại',
                401: 'Chưa xác thực (Missing Token)'
            }
        )
        @namespace.expect(league_input_model, validate=True)
        @jwt_required()
        def post(self):
            """Tạo giải đấu mới (Create)"""
            # Xóa cache danh sách khi có dữ liệu mới
            cache.delete('all_leagues')
            data = request.json
            return league_service.create_league(data)

    @namespace.route('/<int:id>')
    @namespace.param('id', 'ID của giải đấu')
    class LeagueResource(Resource):
        @namespace.doc(
            description='Lấy thông tin chi tiết giải đấu',
            responses={
                200: 'Tìm thấy dữ liệu',
                404: 'Không tìm thấy giải đấu'
            }
        )
        @namespace.marshal_with(league_output_model)
        @cache.cached(timeout=300)  # Cache chi tiết trong 5 phút
        def get(self, id):
            """Lấy chi tiết giải đấu (Read One)"""
            return league_service.get_league_by_id(id)

        @namespace.doc(
            security='jwt',
            description='Cập nhật thông tin giải đấu',
            responses={
                200: 'Cập nhật thành công',
                404: 'Không tìm thấy giải đấu',
                401: 'Chưa xác thực'
            }
        )
        @namespace.expect(league_input_model)
        @jwt_required()
        def put(self, id):
            """Cập nhật giải đấu (Update)"""
            # Xóa cache cũ
            cache.delete('all_leagues')
            cache.delete_memoized(self.get,
                                  id)  # Xóa cache của hàm get theo ID này (nếu library hỗ trợ) hoặc để timeout tự hết

            data = request.json
            return league_service.update_league(id, data)

        @namespace.doc(
            security='jwt',
            description='Xóa giải đấu',
            responses={
                200: 'Xóa thành công',
                404: 'Không tìm thấy giải đấu',
                401: 'Chưa xác thực'
            }
        )
        @jwt_required()
        def delete(self, id):
            """Xóa giải đấu (Delete)"""
            cache.delete('all_leagues')
            return league_service.delete_league(id)