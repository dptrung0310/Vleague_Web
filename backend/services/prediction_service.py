from datetime import datetime
from services.team_service import TeamService 
from models.prediction import Prediction
from models.match import Match
from models.user import User
from extensions import db
from sqlalchemy import desc, and_, or_ 
from models.team import Team  # Thêm import này
from models.stadium import Stadium  # Thêm import này 
from models.season import Season  # Thêm import này
from services.match_service import MatchService

class PredictionService:
    @staticmethod
    def create_prediction(user_id, match_id, data):
        """
        Tạo dự đoán mới cho người dùng
        """
        try:
            print(f"DEBUG: Creating prediction for user={user_id}, match={match_id}")
            
            # Kiểm tra trận đấu có tồn tại
            match = Match.query.get(match_id)
            if not match:
                print(f"DEBUG: Match {match_id} not found")
                return None, "Match not found"
            
            # Kiểm tra trận đấu đã diễn ra chưa (status phải là 'Chưa đá')
            if match.status != 'Chưa đá':
                print(f"DEBUG: Match {match_id} status is {match.status}, not 'Chưa đá'")
                return None, "Cannot predict for finished or ongoing match"
            
            # Kiểm tra người dùng đã dự đoán chưa
            existing_prediction = Prediction.query.filter_by(
                user_id=user_id, 
                match_id=match_id
            ).first()
            
            if existing_prediction:
                print(f"DEBUG: User {user_id} already predicted match {match_id}")
                return None, "Already predicted this match"
            
            # Tạo dự đoán mới
            prediction = Prediction(
                user_id=user_id,
                match_id=match_id,
                predicted_result=data.get('predicted_result'),
                predicted_home_score=data.get('predicted_home_score'),
                predicted_away_score=data.get('predicted_away_score'),
                predicted_card_over_under=data.get('predicted_card_over_under'),
                status='PENDING'
            )
            
            db.session.add(prediction)
            db.session.commit()
            
            print(f"DEBUG: Prediction created successfully with ID {prediction.prediction_id}")
            return prediction, None
            
        except Exception as e:
            db.session.rollback()
            print(f"DEBUG: Error creating prediction: {str(e)}")
            return None, str(e)
        
    @staticmethod
    def update_prediction(prediction_id, user_id, data):
        """
        Cập nhật dự đoán (chỉ khi trận chưa bắt đầu)
        """
        try:
            print(f"DEBUG: Updating prediction {prediction_id}")
            print(f"DEBUG: Data received: {data}")
            
            prediction = Prediction.query.get(prediction_id)
            if not prediction:
                return None, "Prediction not found"
            
            # Kiểm tra quyền sở hữu
            if prediction.user_id != int(user_id):
                return None, "Unauthorized"
            
            # Kiểm tra trận đấu
            match = Match.query.get(prediction.match_id)
            if match.status != 'Chưa đá':
                return None, "Cannot update prediction for finished match"
            
            # Cập nhật kết quả
            if 'predicted_result' in data:
                prediction.predicted_result = data['predicted_result']
            
            # QUAN TRỌNG: Cập nhật tỉ số, cho phép None
            if 'predicted_home_score' in data:
                # Nhận None từ frontend nếu là dự đoán kết quả
                prediction.predicted_home_score = data['predicted_home_score']
            
            if 'predicted_away_score' in data:
                prediction.predicted_away_score = data['predicted_away_score']
            
            if 'predicted_card_over_under' in data:
                prediction.predicted_card_over_under = data['predicted_card_over_under']

            prediction.updated_at = datetime.utcnow()
            db.session.commit()
            
            print(f"DEBUG: Updated prediction: {prediction.to_dict()}")
            return prediction, None
            
        except Exception as e:
            db.session.rollback()
            print(f"DEBUG: Error updating prediction: {str(e)}")
            return None, str(e)
        
    @staticmethod
    def delete_prediction(prediction_id, user_id):
        """
        Xóa dự đoán (chỉ khi trận chưa bắt đầu)
        """
        try:
            print(f"DEBUG: Attempting to delete prediction {prediction_id} for user {user_id}")
            print(f"DEBUG: User ID type: {type(user_id)}")
            
            prediction = Prediction.query.get(prediction_id)
            if not prediction:
                print(f"DEBUG: Prediction {prediction_id} not found")
                return False, "Prediction not found"
            
            # KIỂM TRA QUYỀN SỞ HỮU - chuyển user_id về int để so sánh
            # Vì JWT identity thường trả về string
            try:
                user_id_int = int(user_id)
            except (ValueError, TypeError):
                print(f"DEBUG: Invalid user_id format: {user_id}")
                return False, "Invalid user ID format"
            
            print(f"DEBUG: Prediction user_id: {prediction.user_id} (type: {type(prediction.user_id)})")
            print(f"DEBUG: Current user_id: {user_id_int} (type: {type(user_id_int)})")
            
            if prediction.user_id != user_id_int:
                print(f"DEBUG: Unauthorized: {prediction.user_id} != {user_id_int}")
                return False, "Unauthorized: You don't own this prediction"
            
            # Kiểm tra trận đấu đã bắt đầu chưa
            match = Match.query.get(prediction.match_id)
            if not match:
                print(f"DEBUG: Match {prediction.match_id} not found")
                return False, "Match not found"
            
            print(f"DEBUG: Match status: {match.status}")
            if match.status != 'Chưa đá':
                print(f"DEBUG: Cannot delete. Match status is: {match.status}")
                return False, f"Cannot delete prediction for match that has already started or finished (Status: {match.status})"
            
            print(f"DEBUG: Deleting prediction {prediction_id}...")
            db.session.delete(prediction)
            db.session.commit()
            
            print(f"DEBUG: Prediction {prediction_id} deleted successfully")
            return True, None
            
        except Exception as e:
            db.session.rollback()
            print(f"DEBUG: Error deleting prediction: {str(e)}")
            import traceback
            traceback.print_exc()
            return False, str(e)
        
    @staticmethod
    def get_user_predictions(user_id, page=1, per_page=20):
        """
        Lấy tất cả dự đoán của người dùng
        """
        try:
            pagination = Prediction.query.filter_by(
                user_id=user_id
            ).order_by(
                desc(Prediction.created_at)
            ).paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
            
            return pagination, None
            
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def get_match_predictions(match_id):
        """
        Lấy tất cả dự đoán cho một trận đấu
        """
        try:
            predictions = Prediction.query.filter_by(
                match_id=match_id
            ).order_by(
                desc(Prediction.created_at)
            ).all()
            
            return predictions, None
            
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def get_upcoming_matches_for_prediction(user_id=None):
        """
        Lấy danh sách TẤT CẢ trận sắp diễn ra để dự đoán
        KHÔNG phân trang - load tất cả trận có status = 'Chưa đá' của mùa hiện tại
        """
        try:
            MatchService.update_match_statuses()
            print(f"DEBUG: Getting ALL upcoming matches for user_id={user_id}")
            
            # 1. Lấy season_id lớn nhất (mùa hiện tại)
            current_season = Season.query.order_by(desc(Season.season_id)).first()
            if not current_season:
                return None, "Không tìm thấy mùa giải nào"
            
            current_season_id = current_season.season_id
            print(f"DEBUG: Current season_id = {current_season_id}")

            now = datetime.utcnow()

            matches_to_start = Match.query.filter(
                Match.season_id == current_season_id,
                Match.status.in_(['Chưa đá', 'Đang diễn ra']),
                Match.match_datetime <= now
            ).all()
            
            if matches_to_start:
                print(f"DEBUG: Auto-starting {len(matches_to_start)} matches...")
                for match in matches_to_start:
                    match.status = 'Đang diễn ra'
                db.session.commit()
            
            # 2. Lấy trận đấu: Bao gồm cả 'Chưa đá' VÀ 'Đang diễn ra'
            matches = Match.query.filter(
                Match.season_id == current_season_id,
                Match.status.in_(['Chưa đá', 'Đang diễn ra'])
            ).order_by(Match.match_datetime.asc()).all()
            
            print(f"DEBUG: Found {len(matches)} matches with status 'Chưa đá' or 'Đang diễn ra' in season {current_season_id}")
            
            # 3. Chuẩn bị dữ liệu trả về
            matches_data = []
            
            for match in matches:
                # Lấy thông tin cơ bản của trận
                match_dict = {
                    'match_id': match.match_id,
                    'season_id': match.season_id,
                    'round': match.round,
                    'match_datetime': match.match_datetime.isoformat() if match.match_datetime else None,
                    'home_team_id': match.home_team_id,
                    'away_team_id': match.away_team_id,
                    'home_score': match.home_score,
                    'away_score': match.away_score,
                    'status': match.status,
                    'stadium_id': match.stadium_id,
                    'match_url': match.match_url,
                    'season_name': match.season.name if match.season else None,
                    'home_team_name': match.home_team.name if match.home_team else None,
                    'away_team_name': match.away_team.name if match.away_team else None,
                    'stadium_name': match.stadium.name if match.stadium else None,
                }
                
                # Thêm logo nếu có
                # Xử lý logo cho đội nhà
                if match.home_team and hasattr(match.home_team, 'logo_url'):
                    match_dict['home_team_logo'] = TeamService._process_logo_url(match.home_team.logo_url)
                else:
                    match_dict['home_team_logo'] = None
                    
                # Xử lý logo cho đội khách
                if match.away_team and hasattr(match.away_team, 'logo_url'):
                    match_dict['away_team_logo'] = TeamService._process_logo_url(match.away_team.logo_url)
                else:
                    match_dict['away_team_logo'] = None
                
                # Nếu có user_id, kiểm tra xem đã dự đoán chưa
                if user_id:
                    prediction = Prediction.query.filter_by(
                        user_id=user_id,
                        match_id=match.match_id
                    ).first()
                    
                    if prediction:
                        match_dict['prediction_id'] = prediction.prediction_id
                        match_dict['predicted_result'] = prediction.predicted_result
                        match_dict['predicted_home_score'] = prediction.predicted_home_score
                        match_dict['predicted_away_score'] = prediction.predicted_away_score
                        match_dict['predicted_card_over_under'] = prediction.predicted_card_over_under
                        match_dict['prediction_status'] = prediction.status
                
                matches_data.append(match_dict)
            
            print(f"DEBUG: Returning {len(matches_data)} matches (ALL matches, no pagination)")
            
            return {
                'matches': matches_data,
                'total': len(matches_data)
            }, None
                
        except Exception as e:
            print(f"DEBUG: Error in get_upcoming_matches_for_prediction: {str(e)}")
            import traceback
            traceback.print_exc()
            return None, str(e)
         
    @staticmethod
    def calculate_points_and_update(prediction):
        """
        Tính điểm và cập nhật dự đoán sau khi trận kết thúc
        """
        try:
            match = prediction.match
            
            if match.status != 'Kết thúc':
                return 0, "Match not finished yet"
            
            # Tính điểm
            points = 0
            
            # Điểm cho dự đoán kết quả (thắng/thua/hòa)
            actual_result = None
            if match.home_score > match.away_score:
                actual_result = 'HOME_WIN'
            elif match.home_score < match.away_score:
                actual_result = 'AWAY_WIN'
            else:
                actual_result = 'DRAW'
            
            if prediction.predicted_result == actual_result:
                points += 3  # Điểm cho dự đoán đúng kết quả
            
            # Điểm cho dự đoán tỉ số chính xác
            if (prediction.predicted_home_score == match.home_score and 
                prediction.predicted_away_score == match.away_score):
                points += 5  # Bonus cho dự đoán đúng tỉ số
            
            # Điểm cho dự đoán gần đúng (sai lệch 1 bàn)
            elif (abs(prediction.predicted_home_score - match.home_score) <= 1 and 
                  abs(prediction.predicted_away_score - match.away_score) <= 1):
                points += 2  # Bonus cho dự đoán gần đúng
            
            # Cập nhật điểm và trạng thái
            prediction.points_awarded = points
            prediction.status = 'CORRECT' if points > 0 else 'INCORRECT'
            
            # Cập nhật thống kê người dùng
            user = User.query.get(prediction.user_id)
            user.points += points
            user.total_predictions += 1
            if points > 0:
                user.correct_predictions += 1
            
            db.session.commit()
            
            return points, None
            
        except Exception as e:
            db.session.rollback()
            return 0, str(e)