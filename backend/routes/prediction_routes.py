from flask import Blueprint, request, jsonify
from services.prediction_service import PredictionService

prediction_bp = Blueprint('predictions', __name__)

@prediction_bp.route('/predictions', methods=['GET'])
def get_predictions():
    user_id = request.args.get('user_id', type=int)
    match_id = request.args.get('match_id', type=int)
    
    if user_id:
        predictions = PredictionService.get_predictions_by_user(user_id)
    elif match_id:
        predictions = PredictionService.get_predictions_by_match(match_id)
    else:
        predictions = PredictionService.get_all_predictions()
    
    return jsonify(predictions)

@prediction_bp.route('/predictions/<int:prediction_id>', methods=['GET'])
def get_prediction(prediction_id):
    prediction = PredictionService.get_prediction_by_id(prediction_id)
    if not prediction:
        return jsonify({'error': 'Prediction not found'}), 404
    return jsonify(prediction)

@prediction_bp.route('/predictions', methods=['POST'])
def create_prediction():
    data = request.json
    
    required_fields = ['user_id', 'match_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Kiểm tra ít nhất phải có predicted_result hoặc cả hai score
    if 'predicted_result' not in data and ('predicted_home_score' not in data or 'predicted_away_score' not in data):
        return jsonify({'error': 'Either predicted_result or both scores are required'}), 400
    
    prediction, error = PredictionService.create_prediction(data)
    if error:
        return jsonify({'error': error}), 400
    
    if prediction:
        return jsonify(prediction), 201
    return jsonify({'error': 'Failed to create prediction'}), 500

@prediction_bp.route('/predictions/<int:prediction_id>', methods=['PUT'])
def update_prediction(prediction_id):
    data = request.json
    
    prediction, error = PredictionService.update_prediction(prediction_id, data)
    if error:
        return jsonify({'error': error}), 400
    
    if not prediction:
        return jsonify({'error': 'Prediction not found'}), 404
    
    return jsonify(prediction)

@prediction_bp.route('/predictions/<int:prediction_id>', methods=['DELETE'])
def delete_prediction(prediction_id):
    success, error = PredictionService.delete_prediction(prediction_id)
    if error:
        return jsonify({'error': error}), 400
    
    if not success:
        return jsonify({'error': 'Prediction not found'}), 404
    
    return jsonify({'message': 'Prediction deleted successfully'}), 200

@prediction_bp.route('/predictions/calculate/<int:match_id>', methods=['POST'])
def calculate_points(match_id):
    success, message = PredictionService.calculate_prediction_points(match_id)
    
    if success:
        return jsonify({'message': message}), 200
    else:
        return jsonify({'error': message}), 400

@prediction_bp.route('/predictions/upcoming/<int:user_id>', methods=['GET'])
def get_upcoming_matches(user_id):
    days_ahead = request.args.get('days', default=7, type=int)
    
    matches = PredictionService.get_upcoming_matches_for_prediction(user_id, days_ahead)
    return jsonify(matches)