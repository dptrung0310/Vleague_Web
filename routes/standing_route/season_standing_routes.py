from flask import request
from flask_restx import Resource, reqparse
from flask_jwt_extended import jwt_required
from extensions import cache
from services.standing_service.season_standing_service import SeasonStandingService


def init_season_standing_routes(api, namespace, schemas):
    service = SeasonStandingService()

    output_model = schemas['standing_output']
    input_model = schemas['standing_input']

    # Parser để lấy query params (ví dụ: ?round=5)
    parser = reqparse.RequestParser()
    parser.add_argument('round', type=int, help='Lọc theo vòng đấu (Option)')

    @namespace.route('/season/<int:season_id>')
    @namespace.param('season_id', 'ID Mùa giải')
    class StandingList(Resource):
        @namespace.doc('get_standings')
        @namespace.expect(parser)
        @namespace.marshal_list_with(output_model)
        @cache.cached(timeout=60, query_string=True)  # Cache theo cả query string (round)
        def get(self, season_id):
            """Xem bảng xếp hạng của mùa giải"""
            args = parser.parse_args()
            round_num = args.get('round')
            return service.get_standings(season_id, round_num)

    @namespace.route('')
    class StandingCreate(Resource):
        @namespace.doc('create_standing_entry', security='jwt')
        @namespace.expect(input_model, validate=True)
        @jwt_required()
        def post(self):
            """Nhập kết quả xếp hạng cho 1 đội (thường dùng script tự động tính sau mỗi trận)"""
            # Xóa cache liên quan đến mùa giải này (cần logic phức tạp hơn để clear đúng key, tạm thời clear hết)
            cache.clear()
            return service.create_standing_entry(request.json)

    @namespace.route('/<int:id>')
    @namespace.param('id', 'Standing Entry ID')
    class StandingResource(Resource):
        @namespace.doc('update_standing_entry', security='jwt')
        @namespace.expect(input_model)
        @jwt_required()
        def put(self, id):
            """Cập nhật thông tin xếp hạng"""
            cache.clear()
            return service.update_standing_entry(id, request.json)

        @namespace.doc('delete_standing_entry', security='jwt')
        @jwt_required()
        def delete(self, id):
            """Xóa dòng xếp hạng"""
            cache.clear()
            return service.delete_standing_entry(id)