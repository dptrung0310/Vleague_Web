from flask import request
from flask_restx import Resource
from flask_jwt_extended import jwt_required
from extensions import cache
from services.core_services.stadium_service import StadiumService


def init_stadium_routes(api, namespace, schemas):
    """Khởi tạo các route cho Sân vận động (Stadium)"""
    stadium_service = StadiumService()

    stadium_output_model = schemas['stadium_output']
    stadium_input_model = schemas['stadium_input']

    @namespace.route('')
    class StadiumList(Resource):
        @namespace.doc(
            description='Lấy danh sách tất cả sân vận động',
            responses={200: 'Thành công'}
        )
        @namespace.marshal_list_with(stadium_output_model)
        @cache.cached(timeout=600, key_prefix='all_stadiums')  # Sân ít khi thay đổi, cache 10 phút
        def get(self):
            """Lấy danh sách sân vận động (Read All)"""
            return stadium_service.get_all_stadiums()

        @namespace.doc(
            security='jwt',
            description='Thêm sân vận động mới',
            responses={
                201: 'Tạo thành công',
                401: 'Chưa xác thực',
                500: 'Lỗi server'
            }
        )
        @namespace.expect(stadium_input_model, validate=True)
        @jwt_required()
        def post(self):
            """Thêm sân vận động mới (Create)"""
            cache.delete('all_stadiums')
            data = request.json
            return stadium_service.create_stadium(data)

    @namespace.route('/<int:id>')
    @namespace.param('id', 'ID của sân vận động')
    class StadiumResource(Resource):
        @namespace.doc(
            description='Lấy thông tin chi tiết sân vận động',
            responses={200: 'Thành công', 404: 'Không tìm thấy'}
        )
        @namespace.marshal_with(stadium_output_model)
        @cache.cached(timeout=300)
        def get(self, id):
            """Lấy chi tiết sân vận động (Read One)"""
            return stadium_service.get_stadium_by_id(id)

        @namespace.doc(
            security='jwt',
            description='Cập nhật thông tin sân vận động',
            responses={200: 'Cập nhật thành công', 404: 'Không tìm thấy'}
        )
        @namespace.expect(stadium_input_model)
        @jwt_required()
        def put(self, id):
            """Cập nhật sân vận động (Update)"""
            cache.delete('all_stadiums')
            data = request.json
            return stadium_service.update_stadium(id, data)

        @namespace.doc(
            security='jwt',
            description='Xóa sân vận động',
            responses={200: 'Xóa thành công', 404: 'Không tìm thấy'}
        )
        @jwt_required()
        def delete(self, id):
            """Xóa sân vận động (Delete)"""
            cache.delete('all_stadiums')
            return stadium_service.delete_stadium(id)