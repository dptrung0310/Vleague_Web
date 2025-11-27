from flask import request
from flask_restx import Resource
from flask_jwt_extended import jwt_required
from extensions import cache
from services.team_player_services.transfer_service import TransferService


def init_transfer_routes(api, namespace, schemas):
    transfer_service = TransferService()

    output_model = schemas['transfer_output']
    input_model = schemas['transfer_input']

    @namespace.route('/season/<int:season_id>')
    @namespace.param('season_id', 'ID Mùa giải')
    class TransferListBySeason(Resource):
        @namespace.doc('get_transfers_by_season')
        @namespace.marshal_list_with(output_model)
        @cache.cached(timeout=60)
        def get(self, season_id):
            """Lấy danh sách chuyển nhượng trong một mùa giải"""
            return transfer_service.get_transfers_by_season(season_id)

    @namespace.route('')
    class TransferCreate(Resource):
        @namespace.doc('create_transfer', security='jwt')
        @namespace.expect(input_model, validate=True)
        @jwt_required()
        def post(self):
            """Ghi nhận một vụ chuyển nhượng mới"""
            return transfer_service.create_transfer(request.json)

    @namespace.route('/<int:id>')
    @namespace.param('id', 'Transfer ID')
    class TransferResource(Resource):
        @namespace.doc('delete_transfer', security='jwt')
        @jwt_required()
        def delete(self, id):
            """Xóa bản ghi chuyển nhượng"""
            return transfer_service.delete_transfer(id)