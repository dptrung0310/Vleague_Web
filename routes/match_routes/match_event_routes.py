from flask import request
from flask_restx import Resource
from flask_jwt_extended import jwt_required
from extensions import cache
from services.match_services.match_event_service import MatchEventService


def init_match_event_routes(api, namespace, schemas):
    service = MatchEventService()

    output_model = schemas['event_output']
    input_model = schemas['event_input']

    @namespace.route('/match/<int:match_id>')
    class EventsByMatch(Resource):
        @namespace.doc('get_events_by_match')
        @namespace.marshal_list_with(output_model)
        def get(self, match_id):
            """Lấy danh sách sự kiện của trận đấu"""
            # Giả định method này tồn tại trong service
            if hasattr(service, 'get_events_by_match'):
                return service.get_events_by_match(match_id)
            return [], 200

    @namespace.route('')
    class CreateEvent(Resource):
        @namespace.doc('create_event', security='jwt')
        @namespace.expect(input_model, validate=True)
        @jwt_required()
        def post(self):
            """Tạo sự kiện mới (Bàn thắng, Thẻ...)"""
            # Giả định method này tồn tại
            return service.create_event(request.json)

    @namespace.route('/<int:id>')
    @namespace.param('id', 'Event ID')
    class EventResource(Resource):
        @namespace.doc('delete_event', security='jwt')
        @jwt_required()
        def delete(self, id):
            """Xóa sự kiện"""
            # Giả định method này tồn tại
            return service.delete_event(id)