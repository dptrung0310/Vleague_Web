from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.prediction_service import PredictionService
from models.prediction import Prediction
from extensions import db

prediction_bp = Blueprint('predictions', __name__)

@prediction_bp.route('/predictions/upcoming', methods=['GET'])
@jwt_required()
def get_upcoming_matches_for_prediction():
    """
    Lấy danh sách TẤT CẢ trận sắp diễn ra để dự đoán
    KHÔNG phân trang - load tất cả
    """
    try:
        current_user_id = get_jwt_identity()
        
        result, error = PredictionService.get_upcoming_matches_for_prediction(
            user_id=current_user_id
        )
        
        if error:
            return jsonify({
                'status': 'error',
                'message': error
            }), 400
        
        return jsonify({
            'status': 'success',
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    
@prediction_bp.route('/predictions', methods=['POST'])
@jwt_required()
def create_prediction():
    """
    Tạo dự đoán mới
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.json
        
        # Validate required fields
        required_fields = ['match_id', 'predicted_result']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        prediction, error = PredictionService.create_prediction(
            user_id=current_user_id,
            match_id=data['match_id'],
            data=data
        )
        
        if error:
            return jsonify({
                'status': 'error',
                'message': error
            }), 400
        
        return jsonify({
            'status': 'success',
            'message': 'Prediction created successfully',
            'data': prediction.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@prediction_bp.route('/predictions/<int:prediction_id>', methods=['PUT'])
@jwt_required()
def update_prediction(prediction_id):
    """
    Cập nhật dự đoán
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.json
        
        print(f"API: Updating prediction {prediction_id} for user {current_user_id}")
        print(f"API: Request data: {data}")
        
        prediction, error = PredictionService.update_prediction(
            prediction_id=prediction_id,
            user_id=current_user_id,
            data=data
        )
        
        if error:
            print(f"API: Update error: {error}")
            return jsonify({
                'status': 'error',
                'message': error
            }), 400
        
        # Đảm bảo trả về đúng cấu trúc
        result = {
            'status': 'success',
            'message': 'Prediction updated successfully',
            'data': prediction.to_dict()  # Đây phải là dictionary
        }
        
        print(f"API: Update successful, returning: {result}")
        return jsonify(result), 200
        
    except Exception as e:
        print(f"API: Exception in update_prediction: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
@prediction_bp.route('/predictions/<int:prediction_id>', methods=['DELETE'])
@jwt_required()
def delete_prediction(prediction_id):
    """
    Xóa dự đoán
    """
    try:
        current_user_id = get_jwt_identity()
        print(f"API DELETE: User {current_user_id} trying to delete prediction {prediction_id}")
        print(f"API DELETE: User ID type from token: {type(current_user_id)}")
        
        success, error = PredictionService.delete_prediction(
            prediction_id=prediction_id,
            user_id=current_user_id
        )
        
        if error:
            print(f"API DELETE: Error - {error}")
            return jsonify({
                'status': 'error',
                'message': error
            }), 400
        
        return jsonify({
            'status': 'success',
            'message': 'Prediction deleted successfully'
        }), 200
        
    except Exception as e:
        print(f"API DELETE: Exception - {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    
@prediction_bp.route('/predictions/user', methods=['GET'])
@jwt_required()
def get_user_predictions():
    """
    Lấy tất cả dự đoán của người dùng hiện tại
    """
    try:
        current_user_id = get_jwt_identity()
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        pagination, error = PredictionService.get_user_predictions(
            user_id=current_user_id,
            page=page,
            per_page=per_page
        )
        
        if error:
            return jsonify({
                'status': 'error',
                'message': error
            }), 400
        
        predictions_data = []
        for prediction in pagination.items:
            pred_dict = prediction.to_dict(include_match=True)
            predictions_data.append(pred_dict)
        
        return jsonify({
            'status': 'success',
            'data': predictions_data,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@prediction_bp.route('/predictions/match/<int:match_id>', methods=['GET'])
def get_match_predictions(match_id):
    """
    Lấy tất cả dự đoán cho một trận đấu (public)
    """
    try:
        predictions, error = PredictionService.get_match_predictions(match_id)
        
        if error:
            return jsonify({
                'status': 'error',
                'message': error
            }), 400
        
        predictions_data = []
        for prediction in predictions:
            pred_dict = prediction.to_dict()
            # Ẩn thông tin nhạy cảm
            pred_dict.pop('user_id', None)
            predictions_data.append(pred_dict)
        
        return jsonify({
            'status': 'success',
            'data': predictions_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@prediction_bp.route('/predictions/check/<int:match_id>', methods=['GET'])
@jwt_required()
def check_user_prediction(match_id):
    """
    Kiểm tra xem người dùng đã dự đoán trận này chưa
    """
    try:
        current_user_id = get_jwt_identity()
        
        prediction = Prediction.query.filter_by(
            user_id=current_user_id,
            match_id=match_id
        ).first()
        
        if prediction:
            return jsonify({
                'status': 'success',
                'has_predicted': True,
                'prediction': prediction.to_dict()
            }), 200
        else:
            return jsonify({
                'status': 'success',
                'has_predicted': False
            }), 200
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500