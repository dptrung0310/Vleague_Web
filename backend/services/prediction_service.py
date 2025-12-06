from extensions import db
from sqlalchemy import text
from datetime import datetime

class PredictionService:
    @staticmethod
    def get_all_predictions():
        try:
            query = text('SELECT * FROM Predictions ORDER BY created_at DESC')
            result = db.session.execute(query)
            
            predictions = []
            for row in result:
                pred_dict = dict(row._mapping)
                # Xử lý datetime
                for field in ['created_at', 'updated_at']:
                    if pred_dict.get(field):
                        if isinstance(pred_dict[field], str):
                            try:
                                pred_dict[field] = datetime.strptime(pred_dict[field], '%Y-%m-%d %H:%M:%S').isoformat()
                            except:
                                pred_dict[field] = None
                        elif hasattr(pred_dict[field], 'isoformat'):
                            pred_dict[field] = pred_dict[field].isoformat()
                predictions.append(pred_dict)
            
            return predictions
        except Exception as e:
            print(f"ERROR in get_all_predictions: {str(e)}")
            return []
    
    @staticmethod
    def get_prediction_by_id(prediction_id):
        try:
            query = text('SELECT * FROM Predictions WHERE prediction_id = :id')
            result = db.session.execute(query, {'id': prediction_id}).fetchone()
            
            if result:
                pred_dict = dict(result._mapping)
                for field in ['created_at', 'updated_at']:
                    if pred_dict.get(field):
                        if isinstance(pred_dict[field], str):
                            try:
                                pred_dict[field] = datetime.strptime(pred_dict[field], '%Y-%m-%d %H:%M:%S').isoformat()
                            except:
                                pred_dict[field] = None
                        elif hasattr(pred_dict[field], 'isoformat'):
                            pred_dict[field] = pred_dict[field].isoformat()
                return pred_dict
            return None
        except Exception as e:
            print(f"ERROR in get_prediction_by_id: {str(e)}")
            return None
    
    @staticmethod
    def create_prediction(data):
        try:
            # Kiểm tra trận đấu có tồn tại và chưa diễn ra không
            match_query = text('SELECT match_datetime, status FROM Matches WHERE match_id = :match_id')
            match_result = db.session.execute(match_query, {'match_id': data['match_id']}).fetchone()
            
            if not match_result:
                return None, "Match not found"
            
            match_time = match_result[0]
            match_status = match_result[1]
            
            # Kiểm tra trận đấu đã diễn ra chưa
            if match_status != 'SCHEDULED':
                return None, "Match has already started or finished"
            
            if isinstance(match_time, str):
                match_time = datetime.strptime(match_time, '%Y-%m-%d %H:%M:%S')
            
            if datetime.utcnow() >= match_time:
                return None, "Match has already started"
            
            # Kiểm tra user đã dự đoán trận này chưa
            existing_query = text('''
                SELECT prediction_id FROM Predictions 
                WHERE user_id = :user_id AND match_id = :match_id
            ''')
            existing = db.session.execute(existing_query, {
                'user_id': data['user_id'],
                'match_id': data['match_id']
            }).fetchone()
            
            if existing:
                return None, "User has already predicted this match"
            
            # Nếu có predicted_home_score và predicted_away_score, tính predicted_result
            if 'predicted_home_score' in data and 'predicted_away_score' in data:
                home_score = data['predicted_home_score']
                away_score = data['predicted_away_score']
                
                if home_score > away_score:
                    data['predicted_result'] = 'HOME_WIN'
                elif home_score < away_score:
                    data['predicted_result'] = 'AWAY_WIN'
                else:
                    data['predicted_result'] = 'DRAW'
            
            columns = []
            values = []
            params = {}
            
            for key, value in data.items():
                columns.append(key)
                values.append(f":{key}")
                params[key] = value
            
            query = text(f'''
                INSERT INTO Predictions ({', '.join(columns)})
                VALUES ({', '.join(values)})
            ''')
            
            db.session.execute(query, params)
            db.session.commit()
            
            # Lấy ID vừa tạo
            last_id = db.session.execute(text('SELECT last_insert_rowid()')).fetchone()[0]
            
            return PredictionService.get_prediction_by_id(last_id), None
        except Exception as e:
            print(f"ERROR in create_prediction: {str(e)}")
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def update_prediction(prediction_id, data):
        try:
            existing = PredictionService.get_prediction_by_id(prediction_id)
            if not existing:
                return None, "Prediction not found"
            
            # Kiểm tra trận đấu đã diễn ra chưa
            match_query = text('SELECT match_datetime FROM Matches WHERE match_id = :match_id')
            match_result = db.session.execute(match_query, {'match_id': existing['match_id']}).fetchone()
            
            if match_result:
                match_time = match_result[0]
                if isinstance(match_time, str):
                    match_time = datetime.strptime(match_time, '%Y-%m-%d %H:%M:%S')
                
                if datetime.utcnow() >= match_time:
                    return None, "Cannot update prediction after match has started"
            
            # Nếu đã có kết quả (status khác PENDING) thì không cho sửa
            if existing['status'] != 'PENDING':
                return None, "Cannot update prediction after match has been processed"
            
            # Tính lại predicted_result nếu có thay đổi tỉ số
            if 'predicted_home_score' in data or 'predicted_away_score' in data:
                home_score = data.get('predicted_home_score', existing['predicted_home_score'])
                away_score = data.get('predicted_away_score', existing['predicted_away_score'])
                
                if home_score > away_score:
                    data['predicted_result'] = 'HOME_WIN'
                elif home_score < away_score:
                    data['predicted_result'] = 'AWAY_WIN'
                else:
                    data['predicted_result'] = 'DRAW'
            
            set_clause = ', '.join([f"{key} = :{key}" for key in data.keys()])
            query = text(f'''
                UPDATE Predictions 
                SET {set_clause}
                WHERE prediction_id = :prediction_id
            ''')
            
            params = data.copy()
            params['prediction_id'] = prediction_id
            
            db.session.execute(query, params)
            db.session.commit()
            
            return PredictionService.get_prediction_by_id(prediction_id), None
        except Exception as e:
            print(f"ERROR in update_prediction: {str(e)}")
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def delete_prediction(prediction_id):
        try:
            existing = PredictionService.get_prediction_by_id(prediction_id)
            if not existing:
                return False, "Prediction not found"
            
            # Kiểm tra trận đấu đã diễn ra chưa
            match_query = text('SELECT match_datetime FROM Matches WHERE match_id = :match_id')
            match_result = db.session.execute(match_query, {'match_id': existing['match_id']}).fetchone()
            
            if match_result:
                match_time = match_result[0]
                if isinstance(match_time, str):
                    match_time = datetime.strptime(match_time, '%Y-%m-%d %H:%M:%S')
                
                if datetime.utcnow() >= match_time:
                    return False, "Cannot delete prediction after match has started"
            
            query = text('DELETE FROM Predictions WHERE prediction_id = :prediction_id')
            db.session.execute(query, {'prediction_id': prediction_id})
            db.session.commit()
            
            return True, None
        except Exception as e:
            print(f"ERROR in delete_prediction: {str(e)}")
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def get_predictions_by_user(user_id):
        try:
            query = text('''
                SELECT p.*, m.home_team_id, m.away_team_id, m.match_datetime,
                       m.home_score, m.away_score, m.status as match_status,
                       ht.name as home_team_name, at.name as away_team_name
                FROM Predictions p
                LEFT JOIN Matches m ON p.match_id = m.match_id
                LEFT JOIN Teams ht ON m.home_team_id = ht.team_id
                LEFT JOIN Teams at ON m.away_team_id = at.team_id
                WHERE p.user_id = :user_id
                ORDER BY m.match_datetime DESC
            ''')
            result = db.session.execute(query, {'user_id': user_id})
            
            predictions = []
            for row in result:
                pred_dict = dict(row._mapping)
                for field in ['created_at', 'updated_at', 'match_datetime']:
                    if pred_dict.get(field):
                        if isinstance(pred_dict[field], str):
                            try:
                                pred_dict[field] = datetime.strptime(pred_dict[field], '%Y-%m-%d %H:%M:%S').isoformat()
                            except:
                                pred_dict[field] = None
                        elif hasattr(pred_dict[field], 'isoformat'):
                            pred_dict[field] = pred_dict[field].isoformat()
                predictions.append(pred_dict)
            
            return predictions
        except Exception as e:
            print(f"ERROR in get_predictions_by_user: {str(e)}")
            return []
    
    @staticmethod
    def get_predictions_by_match(match_id):
        try:
            query = text('''
                SELECT p.*, u.username, u.avatar_url
                FROM Predictions p
                LEFT JOIN Users u ON p.user_id = u.user_id
                WHERE p.match_id = :match_id
                ORDER BY p.created_at DESC
            ''')
            result = db.session.execute(query, {'match_id': match_id})
            
            predictions = []
            for row in result:
                pred_dict = dict(row._mapping)
                for field in ['created_at', 'updated_at']:
                    if pred_dict.get(field):
                        if isinstance(pred_dict[field], str):
                            try:
                                pred_dict[field] = datetime.strptime(pred_dict[field], '%Y-%m-%d %H:%M:%S').isoformat()
                            except:
                                pred_dict[field] = None
                        elif hasattr(pred_dict[field], 'isoformat'):
                            pred_dict[field] = pred_dict[field].isoformat()
                predictions.append(pred_dict)
            
            return predictions
        except Exception as e:
            print(f"ERROR in get_predictions_by_match: {str(e)}")
            return []
    
    @staticmethod
    def calculate_prediction_points(match_id):
        """
        Tính điểm cho các dự đoán của một trận đấu.
        Chỉ nên gọi khi trận đấu đã kết thúc (status = 'FINISHED').
        Logic điểm:
        - Đúng tỉ số: 20 điểm
        - Đúng kết quả (1x2): 10 điểm
        """
        try:
            # Lấy thông tin trận đấu
            match_query = text('''
                SELECT home_score, away_score, status 
                FROM Matches 
                WHERE match_id = :match_id
            ''')
            match_result = db.session.execute(match_query, {'match_id': match_id}).fetchone()
            
            if not match_result:
                return False, "Match not found"
            
            home_score, away_score, status = match_result
            
            if status != 'FINISHED':
                return False, "Match is not finished"
            
            # Xác định kết quả thực tế
            if home_score > away_score:
                actual_result = 'HOME_WIN'
            elif home_score < away_score:
                actual_result = 'AWAY_WIN'
            else:
                actual_result = 'DRAW'
            
            # Lấy tất cả dự đoán cho trận này
            predictions = PredictionService.get_predictions_by_match(match_id)
            
            for pred in predictions:
                prediction_id = pred['prediction_id']
                user_id = pred['user_id']
                predicted_home = pred['predicted_home_score']
                predicted_away = pred['predicted_away_score']
                predicted_result = pred['predicted_result']
                
                points = 0
                pred_status = 'INCORRECT'
                
                # Tính điểm
                if predicted_home == home_score and predicted_away == away_score:
                    points = 20
                    pred_status = 'CORRECT'
                elif predicted_result == actual_result:
                    points = 10
                    pred_status = 'CORRECT'
                
                # Cập nhật bảng Predictions
                update_pred_query = text('''
                    UPDATE Predictions 
                    SET points_awarded = :points, 
                        status = :status,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE prediction_id = :prediction_id
                ''')
                db.session.execute(update_pred_query, {
                    'points': points,
                    'status': pred_status,
                    'prediction_id': prediction_id
                })
                
                # Cập nhật điểm cho user nếu có điểm
                if points > 0:
                    from services.user_service import UserService
                    UserService.update_user_points(user_id, points, is_correct=True)
            
            # Đánh dấu các prediction đã xử lý
            mark_processed_query = text('''
                UPDATE Predictions 
                SET status = 'PROCESSED'
                WHERE match_id = :match_id AND status = 'PENDING'
            ''')
            db.session.execute(mark_processed_query, {'match_id': match_id})
            
            db.session.commit()
            return True, "Points calculated successfully"
        except Exception as e:
            print(f"ERROR in calculate_prediction_points: {str(e)}")
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def get_upcoming_matches_for_prediction(user_id, days_ahead=7):
        """Lấy danh sách trận đấu sắp diễn ra mà user có thể dự đoán"""
        try:
            query = text('''
                SELECT m.*, 
                       ht.name as home_team_name,
                       at.name as away_team_name,
                       s.name as season_name,
                       CASE WHEN p.prediction_id IS NOT NULL THEN 1 ELSE 0 END as has_predicted
                FROM Matches m
                LEFT JOIN Teams ht ON m.home_team_id = ht.team_id
                LEFT JOIN Teams at ON m.away_team_id = at.team_id
                LEFT JOIN Seasons s ON m.season_id = s.season_id
                LEFT JOIN Predictions p ON m.match_id = p.match_id AND p.user_id = :user_id
                WHERE m.status = 'SCHEDULED'
                AND m.match_datetime >= datetime('now')
                AND m.match_datetime <= datetime('now', '+' || :days || ' days')
                ORDER BY m.match_datetime ASC
            ''')
            
            result = db.session.execute(query, {'user_id': user_id, 'days': days_ahead})
            
            matches = []
            for row in result:
                match_dict = dict(row._mapping)
                
                # Xử lý datetime
                if match_dict.get('match_datetime'):
                    if isinstance(match_dict['match_datetime'], str):
                        try:
                            match_dict['match_datetime'] = datetime.strptime(
                                match_dict['match_datetime'], '%Y-%m-%d %H:%M:%S'
                            ).isoformat()
                        except:
                            match_dict['match_datetime'] = None
                    elif hasattr(match_dict['match_datetime'], 'isoformat'):
                        match_dict['match_datetime'] = match_dict['match_datetime'].isoformat()
                
                matches.append(match_dict)
            
            return matches
        except Exception as e:
            print(f"ERROR in get_upcoming_matches_for_prediction: {str(e)}")
            return []