# services/player_statistics_service.py
from extensions import db
from sqlalchemy import text
from datetime import datetime

class PlayerStatisticsService:
    @staticmethod
    def get_players_by_season(season_id, team_id=None):
        """Lấy danh sách cầu thủ theo mùa và đội, kèm thống kê"""
        try:
            # Base query lấy thông tin cầu thủ
            base_query = '''
                SELECT 
                    p.player_id,
                    p.full_name,
                    p.birth_date,
                    p.height_cm,
                    p.weight_kg,
                    p.position,
                    p.image_url,
                    tr.roster_id,
                    tr.shirt_number,
                    t.team_id,
                    t.name as team_name,
                    t.logo_url as team_logo,
                    s.name as season_name
                FROM Players p
                INNER JOIN TeamRosters tr ON p.player_id = tr.player_id
                INNER JOIN Teams t ON tr.team_id = t.team_id
                INNER JOIN Seasons s ON tr.season_id = s.season_id
                WHERE tr.season_id = :season_id
            '''
            
            params = {'season_id': season_id}
            
            if team_id:
                base_query += ' AND tr.team_id = :team_id'
                params['team_id'] = team_id
            
            base_query += ' ORDER BY t.name, p.full_name'
            
            result = db.session.execute(text(base_query), params)
            
            players = []
            for row in result:
                player_dict = dict(row._mapping)
                
                # Xử lý birth_date
                if player_dict.get('birth_date'):
                    if hasattr(player_dict['birth_date'], 'isoformat'):
                        player_dict['birth_date'] = player_dict['birth_date'].isoformat()
                
                # Lấy thống kê cho cầu thủ
                stats = PlayerStatisticsService.get_player_season_stats(
                    player_dict['player_id'], 
                    season_id,
                    player_dict['team_id']
                )
                player_dict['statistics'] = stats
                
                players.append(player_dict)
            
            return players
            
        except Exception as e:
            print(f"ERROR in get_players_by_season: {str(e)}")
            return []
    
    @staticmethod
    def get_player_season_stats(player_id, season_id, team_id):
        """Lấy thống kê của cầu thủ trong mùa"""
        try:
            # Lấy số trận đã đấu
            matches_query = text('''
                SELECT COUNT(DISTINCT m.match_id) as matches_played
                FROM MatchLineups ml
                JOIN Matches m ON ml.match_id = m.match_id
                WHERE ml.player_id = :player_id 
                AND m.season_id = :season_id
                AND ml.team_id = :team_id
                AND m.status = 'FT'
            ''')
            
            matches_result = db.session.execute(matches_query, {
                'player_id': player_id,
                'season_id': season_id,
                'team_id': team_id
            }).fetchone()
            
            matches_played = matches_result.matches_played if matches_result else 0
            
            # Lấy thống kê từ MatchEvents
            events_query = text('''
                SELECT 
                    COUNT(*) as total_events,
                    SUM(CASE WHEN event_type = 'goal' THEN 1 ELSE 0 END) as goals,
                    SUM(CASE WHEN event_type = 'assist' THEN 1 ELSE 0 END) as assists,
                    SUM(CASE WHEN event_type = 'yellow_card' THEN 1 ELSE 0 END) as yellow_cards,
                    SUM(CASE WHEN event_type = 'red_card' THEN 1 ELSE 0 END) as red_cards,
                    SUM(CASE WHEN event_type = 'substitution_in' THEN 1 ELSE 0 END) as substitutions_in,
                    SUM(CASE WHEN event_type = 'substitution_out' THEN 1 ELSE 0 END) as substitutions_out
                FROM MatchEvents me
                JOIN Matches m ON me.match_id = m.match_id
                WHERE me.player_id = :player_id 
                AND m.season_id = :season_id
                AND me.team_id = :team_id
            ''')
            
            events_result = db.session.execute(events_query, {
                'player_id': player_id,
                'season_id': season_id,
                'team_id': team_id
            }).fetchone()
            
            if events_result:
                stats = dict(events_result._mapping)
                # Xử lý None values
                for key in stats:
                    if stats[key] is None:
                        stats[key] = 0
                
                # Thêm số trận đã đấu
                stats['matches_played'] = matches_played
                
                # Tính hiệu suất
                if matches_played > 0:
                    stats['goals_per_match'] = round(stats['goals'] / matches_played, 2)
                    stats['assists_per_match'] = round(stats['assists'] / matches_played, 2)
                else:
                    stats['goals_per_match'] = 0
                    stats['assists_per_match'] = 0
                
                return stats
            else:
                return {
                    'matches_played': matches_played,
                    'total_events': 0,
                    'goals': 0,
                    'assists': 0,
                    'yellow_cards': 0,
                    'red_cards': 0,
                    'substitutions_in': 0,
                    'substitutions_out': 0,
                    'goals_per_match': 0,
                    'assists_per_match': 0
                }
                
        except Exception as e:
            print(f"ERROR in get_player_season_stats: {str(e)}")
            return {
                'matches_played': 0,
                'total_events': 0,
                'goals': 0,
                'assists': 0,
                'yellow_cards': 0,
                'red_cards': 0,
                'substitutions_in': 0,
                'substitutions_out': 0,
                'goals_per_match': 0,
                'assists_per_match': 0
            }
    
    @staticmethod
    def get_player_detailed_stats(player_id, season_id):
        """Lấy thống kê chi tiết của cầu thủ"""
        try:
            # Lấy thông tin cơ bản của cầu thủ
            player_query = text('''
                SELECT p.*, t.name as current_team, t.logo_url as team_logo
                FROM Players p
                LEFT JOIN TeamRosters tr ON p.player_id = tr.player_id 
                    AND tr.season_id = :season_id
                LEFT JOIN Teams t ON tr.team_id = t.team_id
                WHERE p.player_id = :player_id
            ''')
            
            player_result = db.session.execute(player_query, {
                'player_id': player_id,
                'season_id': season_id
            }).fetchone()
            
            if not player_result:
                return None
            
            player_data = dict(player_result._mapping)
            
            # Lấy lịch sử đội bóng
            team_history_query = text('''
                SELECT 
                    tr.season_id,
                    s.name as season_name,
                    t.name as team_name,
                    t.logo_url as team_logo,
                    tr.shirt_number
                FROM TeamRosters tr
                JOIN Seasons s ON tr.season_id = s.season_id
                JOIN Teams t ON tr.team_id = t.team_id
                WHERE tr.player_id = :player_id
                ORDER BY s.start_date DESC
            ''')
            
            team_history = db.session.execute(team_history_query, {
                'player_id': player_id
            }).fetchall()
            
            player_data['team_history'] = [
                dict(row._mapping) for row in team_history
            ]
            
            # Lấy thống kê tổng hợp tất cả các mùa
            career_stats_query = text('''
                SELECT 
                    COUNT(DISTINCT m.match_id) as career_matches,
                    SUM(CASE WHEN me.event_type = 'goal' THEN 1 ELSE 0 END) as career_goals,
                    SUM(CASE WHEN me.event_type = 'assist' THEN 1 ELSE 0 END) as career_assists
                FROM MatchEvents me
                JOIN Matches m ON me.match_id = m.match_id
                WHERE me.player_id = :player_id
            ''')
            
            career_stats_result = db.session.execute(career_stats_query, {
                'player_id': player_id
            }).fetchone()
            
            if career_stats_result:
                career_stats = dict(career_stats_result._mapping)
                for key in career_stats:
                    if career_stats[key] is None:
                        career_stats[key] = 0
                player_data['career_stats'] = career_stats
            
            return player_data
            
        except Exception as e:
            print(f"ERROR in get_player_detailed_stats: {str(e)}")
            return None