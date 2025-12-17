from datetime import datetime
from models.match import Match
from models.match_referee import MatchReferee
from models.match_lineup import MatchLineup
from models.match_event import MatchEvent
from extensions import db
from sqlalchemy import or_, text, desc

class MatchService:
    @staticmethod
    def get_matches_paginated(page=1, per_page=10):
        """
        Lấy danh sách trận đấu có phân trang, sắp xếp mới nhất lên đầu
        """
        try:
            pagination = Match.query.order_by(
                desc(Match.match_datetime)
            ).paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
            return pagination, None
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def get_all_matches():
        return Match.query.order_by(desc(Match.match_datetime)).all()
    
    @staticmethod
    def get_match_by_id(match_id):
        return Match.query.get(match_id)
    
    @staticmethod
    def create_match(data):
        match = Match(**data)
        db.session.add(match)
        db.session.commit()
        return match
    
    @staticmethod
    def update_match(match_id, data):
        match = Match.query.get(match_id)
        if not match:
            return None
        
        for key, value in data.items():
            setattr(match, key, value)
        
        db.session.commit()
        return match
    
    @staticmethod
    def delete_match(match_id):
        match = Match.query.get(match_id)
        if not match:
            return False
        
        db.session.delete(match)
        db.session.commit()
        return True
    
    @staticmethod
    def get_team_matches(team_id):
        return Match.query.filter(
            or_(Match.home_team_id == team_id, Match.away_team_id == team_id)
        ).all()
    
    @staticmethod
    def add_match_referee(match_id, referee_id, role):
        match_referee = MatchReferee(
            match_id=match_id,
            referee_id=referee_id,
            role=role
        )
        db.session.add(match_referee)
        db.session.commit()
        return match_referee
    
    @staticmethod
    def add_match_lineup(data):
        lineup = MatchLineup(**data)
        db.session.add(lineup)
        db.session.commit()
        return lineup
    
    @staticmethod
    def add_match_event(data):
        event = MatchEvent(**data)
        db.session.add(event)
        db.session.commit()
        return event
    
    @staticmethod
    def get_match_lineups(match_id):
        return MatchLineup.query.filter_by(match_id=match_id).all()
    
    @staticmethod
    def get_match_events(match_id):
        return MatchEvent.query.filter_by(match_id=match_id).all()
    
   # match_service.py - Sửa hàm get_match_with_details với debug chi tiết
    @staticmethod
    def get_match_with_details(match_id):
        try:
            match = Match.query.get(match_id)
            if not match:
                print(f"❌ DEBUG: Match {match_id} không tồn tại trong bảng Matches")
                return None
            
            # Sử dụng SQL query đơn giản hơn để debug
            from sqlalchemy import text
            
            # Query cơ bản để lấy thông tin match
            base_query = text('''
                SELECT 
                    m.match_id,
                    m.home_score,
                    m.away_score,
                    m.round,
                    m.status,
                    s.name as season_name,
                    ht.name as home_team_name,
                    at.name as away_team_name,
                    st.name as stadium_name
                FROM Matches m
                LEFT JOIN Seasons s ON m.season_id = s.season_id
                LEFT JOIN Teams ht ON m.home_team_id = ht.team_id
                LEFT JOIN Teams at ON m.away_team_id = at.team_id
                LEFT JOIN Stadiums st ON m.stadium_id = st.stadium_id
                WHERE m.match_id = :match_id
            ''')
            
            result = db.session.execute(base_query, {'match_id': match_id}).fetchone()
            
            if not result:
                print(f"❌ DEBUG: Query cơ bản không trả về kết quả cho match {match_id}")
                return None
            
            match_data = dict(result._mapping)
            
            # Lấy events
            events_query = text('''
                SELECT COUNT(*) as count FROM MatchEvents WHERE match_id = :match_id
            ''')
            events_count = db.session.execute(events_query, {'match_id': match_id}).fetchone()[0]
            
            events_query = text('''
                SELECT 
                    me.*,
                    p.full_name as player_name,
                    t.name as team_name
                FROM MatchEvents me
                LEFT JOIN Players p ON me.player_id = p.player_id
                LEFT JOIN Teams t ON me.team_id = t.team_id
                WHERE me.match_id = :match_id
                ORDER BY me.minute
            ''')
            events = db.session.execute(events_query, {'match_id': match_id}).fetchall()
            match_data['events'] = [dict(event._mapping) for event in events]
            
            # Lấy lineups
            lineups_query = text('''
                SELECT COUNT(*) as count FROM MatchLineups WHERE match_id = :match_id
            ''')
            lineups_count = db.session.execute(lineups_query, {'match_id': match_id}).fetchone()[0]
            
            lineups_query = text('''
                SELECT 
                    ml.*,
                    p.full_name as player_name,
                    t.name as team_name
                FROM MatchLineups ml
                LEFT JOIN Players p ON ml.player_id = p.player_id
                LEFT JOIN Teams t ON ml.team_id = t.team_id
                WHERE ml.match_id = :match_id
                ORDER BY ml.is_starter DESC, ml.shirt_number
            ''')
            lineups = db.session.execute(lineups_query, {'match_id': match_id}).fetchall()
            match_data['lineups'] = [dict(lineup._mapping) for lineup in lineups]
            
            # Lấy referees
            referees_query = text('''
                SELECT COUNT(*) as count FROM Match_Referees WHERE match_id = :match_id
            ''')
            referees_count = db.session.execute(referees_query, {'match_id': match_id}).fetchone()[0]
            
            referees_query = text('''
                SELECT 
                    mr.*,
                    r.full_name as referee_name
                FROM Match_Referees mr
                LEFT JOIN Referees r ON mr.referee_id = r.referee_id
                WHERE mr.match_id = :match_id
            ''')
            referees = db.session.execute(referees_query, {'match_id': match_id}).fetchall()
            match_data['referees'] = [dict(referee._mapping) for referee in referees]
            
            return match_data
            
        except Exception as e:
            print(f"❌ DEBUG: Lỗi trong get_match_with_details: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
        
    @staticmethod
    def update_match_statuses():
        """
        Tự động cập nhật trạng thái 'Chưa đá' -> 'Đang diễn ra'
        """
        try:
            # SỬA LẠI: Dùng now() thay vì utcnow() để khớp với giờ máy tính của bạn
            now = datetime.now() 
            
            # Debug để bạn kiểm tra giờ server đang hiểu là mấy giờ
            print(f"🕒 SERVER TIME CHECK: {now}")
            
            # Tìm các trận 'Chưa đá' mà thời gian <= hiện tại
            matches_to_start = Match.query.filter(
                Match.status == 'Chưa đá',
                Match.match_datetime <= now
            ).all()
            
            if matches_to_start:
                print(f"🔄 SYSTEM: Phát hiện {len(matches_to_start)} trận cần cập nhật!")
                for match in matches_to_start:
                    print(f"   -> Cập nhật trận: {match.home_team_id} vs {match.away_team_id} (Giờ đá: {match.match_datetime})")
                    match.status = 'Đang diễn ra'
                    
                    # Set tỉ số mặc định 0-0 nếu chưa có
                    if match.home_score is None: match.home_score = 0
                    if match.away_score is None: match.away_score = 0
                
                db.session.commit()
                print("✅ Đã lưu vào Database thành công.")
                return True
            
            return False
        except Exception as e:
            print(f"❌ LỖI UPDATE STATUS: {str(e)}")
            db.session.rollback()
            return False
        """
        Kiểm tra và cập nhật trạng thái các trận đấu đã đến giờ
        """
        try:
            # Lấy thời gian hiện tại
            # Lưu ý: Đảm bảo server và DB cùng múi giờ (UTC hoặc Local)
            # Nếu DB lưu giờ VN thì dùng datetime.now()
            now = datetime.now() 
            
            # Tìm các trận 'Chưa đá' mà thời gian đã qua -> Update thành 'Đang diễn ra'
            matches_to_start = Match.query.filter(
                Match.status == 'Chưa đá',
                Match.match_datetime <= now
            ).all()
            
            if matches_to_start:
                print(f"🔄 SYSTEM: Tự động bắt đầu {len(matches_to_start)} trận đấu...")
                for match in matches_to_start:
                    match.status = 'Đang diễn ra'
                    # Có thể set mặc định tỉ số 0-0 nếu muốn
                    if match.home_score is None: match.home_score = 0
                    if match.away_score is None: match.away_score = 0
                    
                db.session.commit()
                return True
            return False
        except Exception as e:
            print(f"❌ Error updating match statuses: {str(e)}")
            db.session.rollback()
            return False