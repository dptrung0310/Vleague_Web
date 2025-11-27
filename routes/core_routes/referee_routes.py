from flask import request
from flask_restx import Resource
from flask_jwt_extended import jwt_required
from extensions import cache
from services.core_services.referee_service import RefereeService


def init_referee_routes(api, namespace, schemas):
    """Khởi tạo các route cho Trọng tài (Referee)"""
    referee_service = RefereeService()

    referee_output_model = schemas['referee_output']
    referee_input_model = schemas['referee_input']

    @namespace.route('')
    class RefereeList(Resource):
        @namespace.doc(
            description='Lấy danh sách tất cả trọng tài',
            responses={200: 'Thành công'}
        )
        @namespace.marshal_list_with(referee_output_model)
        @cache.cached(timeout=300, key_prefix='all_referees')  # Cache lâu hơn vì ít thay đổi
        def get(self):
            """Lấy danh sách trọng tài (Read All)"""
            return referee_service.get_all_referees()

        @namespace.doc(
            security='jwt',
            description='Thêm trọng tài mới',
            responses={
                201: 'Tạo thành công',
                409: 'Tên đã tồn tại',
                401: 'Chưa xác thực'
            }
        )
        @namespace.expect(referee_input_model, validate=True)
        @jwt_required()
        def post(self):
            """Thêm trọng tài mới (Create)"""
            cache.delete('all_referees')
            data = request.json
            return referee_service.create_referee(data)

    @namespace.route('/<int:id>')
    @namespace.param('id', 'ID của trọng tài')
    class RefereeResource(Resource):
        @namespace.doc(
            description='Lấy thông tin chi tiết trọng tài',
            responses={200: 'Thành công', 404: 'Không tìm thấy'}
        )
        @namespace.marshal_with(referee_output_model)
        @cache.cached(timeout=300)
        def get(self, id):
            """Lấy chi tiết trọng tài (Read One)"""
            return referee_service.get_referee_by_id(id)

        @namespace.doc(
            security='jwt',
            description='Cập nhật thông tin trọng tài',
            responses={200: 'Cập nhật thành công', 404: 'Không tìm thấy'}
        )
        @namespace.expect(referee_input_model)
        @jwt_required()
        def put(self, id):
            """Cập nhật trọng tài (Update)"""
            cache.delete('all_referees')
            data = request.json
            return referee_service.update_referee(id, data)

        @namespace.doc(
            security='jwt',
            description='Xóa trọng tài',
            responses={200: 'Xóa thành công', 404: 'Không tìm thấy'}
        )
        @jwt_required()
        def delete(self, id):
            """Xóa trọng tài (Delete)"""
            cache.delete('all_referees')
            return referee_service.delete_referee(id)