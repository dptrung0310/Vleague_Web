from extensions import db
from sqlalchemy import text

class TeamService:
    @staticmethod
    def get_all_teams(include_stadium=False):
        try:
            if include_stadium:
                query = text('''
                    SELECT t.*, s.name as stadium_name, s.city as stadium_city,
                           s.address as stadium_address, s.latitude, s.longitude
                    FROM Teams t
                    LEFT JOIN Stadiums s ON t.home_stadium_id = s.stadium_id
                    ORDER BY t.name
                ''')
                result = db.session.execute(query)
                
                teams = []
                for row in result:
                    team_dict = dict(row._mapping)
                    
                    # Tách stadium info
                    stadium_info = {}
                    if team_dict.get('home_stadium_id'):
                        stadium_info = {
                            'stadium_id': team_dict['home_stadium_id'],
                            'name': team_dict.get('stadium_name'),
                            'city': team_dict.get('stadium_city'),
                            'address': team_dict.get('stadium_address'),
                            'latitude': float(team_dict['latitude']) if team_dict.get('latitude') else None,
                            'longitude': float(team_dict['longitude']) if team_dict.get('longitude') else None
                        }
                        # Xóa các trường stadium khỏi team dict
                        for field in ['stadium_name', 'stadium_city', 'stadium_address', 'latitude', 'longitude']:
                            team_dict.pop(field, None)
                    
                    team_dict['home_stadium'] = stadium_info if stadium_info else None
                    teams.append(team_dict)
                
                return teams
            else:
                query = text('SELECT * FROM Teams ORDER BY name')
                result = db.session.execute(query)
                
                return [dict(row._mapping) for row in result]
            
        except Exception as e:
            print(f"ERROR in get_all_teams: {str(e)}")
            return []
    
    @staticmethod
    def get_team_by_id(team_id, include_stadium=False):
        try:
            if include_stadium:
                query = text('''
                    SELECT t.*, s.name as stadium_name, s.city as stadium_city,
                           s.address as stadium_address, s.latitude, s.longitude
                    FROM Teams t
                    LEFT JOIN Stadiums s ON t.home_stadium_id = s.stadium_id
                    WHERE t.team_id = :id
                ''')
                result = db.session.execute(query, {'id': team_id}).fetchone()
                
                if result:
                    team_dict = dict(result._mapping)
                    
                    stadium_info = {}
                    if team_dict.get('home_stadium_id'):
                        stadium_info = {
                            'stadium_id': team_dict['home_stadium_id'],
                            'name': team_dict.get('stadium_name'),
                            'city': team_dict.get('stadium_city'),
                            'address': team_dict.get('stadium_address'),
                            'latitude': float(team_dict['latitude']) if team_dict.get('latitude') else None,
                            'longitude': float(team_dict['longitude']) if team_dict.get('longitude') else None
                        }
                        for field in ['stadium_name', 'stadium_city', 'stadium_address', 'latitude', 'longitude']:
                            team_dict.pop(field, None)
                    
                    team_dict['home_stadium'] = stadium_info if stadium_info else None
                    return team_dict
            else:
                query = text('SELECT * FROM Teams WHERE team_id = :id')
                result = db.session.execute(query, {'id': team_id}).fetchone()
                
                return dict(result._mapping) if result else None
            
            return None
            
        except Exception as e:
            print(f"ERROR in get_team_by_id: {str(e)}")
            return None
    
    @staticmethod
    def create_team(data):
        try:
            columns = []
            values = []
            params = {}
            
            for key, value in data.items():
                columns.append(key)
                values.append(f":{key}")
                params[key] = value
            
            query = text(f'''
                INSERT INTO Teams ({', '.join(columns)})
                VALUES ({', '.join(values)})
            ''')
            
            db.session.execute(query, params)
            db.session.commit()
            
            # Lấy ID vừa tạo
            last_id = db.session.execute(text('SELECT last_insert_rowid()')).fetchone()[0]
            
            return TeamService.get_team_by_id(last_id)
            
        except Exception as e:
            print(f"ERROR in create_team: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def update_team(team_id, data):
        try:
            existing = TeamService.get_team_by_id(team_id)
            if not existing:
                return None
            
            set_clause = ', '.join([f"{key} = :{key}" for key in data.keys()])
            query = text(f'''
                UPDATE Teams 
                SET {set_clause}
                WHERE team_id = :team_id
            ''')
            
            params = data.copy()
            params['team_id'] = team_id
            
            db.session.execute(query, params)
            db.session.commit()
            
            return TeamService.get_team_by_id(team_id)
            
        except Exception as e:
            print(f"ERROR in update_team: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def delete_team(team_id):
        try:
            existing = TeamService.get_team_by_id(team_id)
            if not existing:
                return False
            
            query = text('DELETE FROM Teams WHERE team_id = :team_id')
            db.session.execute(query, {'team_id': team_id})
            db.session.commit()
            
            return True
            
        except Exception as e:
            print(f"ERROR in delete_team: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def search_teams(name=None, city=None):
        try:
            query = '''
                SELECT t.*, s.city as stadium_city
                FROM Teams t
                LEFT JOIN Stadiums s ON t.home_stadium_id = s.stadium_id
                WHERE 1=1
            '''
            params = {}
            
            if name:
                query += ' AND t.name LIKE :name'
                params['name'] = f'%{name}%'
            
            if city:
                query += ' AND s.city = :city'
                params['city'] = city
            
            query += ' ORDER BY t.name'
            
            result = db.session.execute(text(query), params)
            
            return [dict(row._mapping) for row in result]
            
        except Exception as e:
            print(f"ERROR in search_teams: {str(e)}")
            return []
    
    @staticmethod
    def get_teams_by_season(season_id):
        """Lấy danh sách đội theo mùa với thông tin standing"""
        try:
            # Lấy vòng đấu mới nhất của mùa
            latest_round_query = text('''
                SELECT MAX(round) as max_round 
                FROM SeasonStandings 
                WHERE season_id = :season_id
            ''')
            latest_round_result = db.session.execute(
                latest_round_query, {'season_id': season_id}
            ).fetchone()
            
            latest_round = latest_round_result.max_round if latest_round_result else 1
            
            # Lấy danh sách đội với standing
            query = text('''
                SELECT 
                    t.team_id,
                    t.name,
                    t.logo_url,
                    t.home_stadium_id,
                    ss.position,
                    ss.played,
                    ss.wins,
                    ss.draws,
                    ss.losses,
                    ss.goals_for,
                    ss.goals_against,
                    ss.goal_difference,
                    ss.points,
                    s.name as stadium_name,
                    s.city as stadium_city,
                    s.address as stadium_address
                FROM Teams t
                LEFT JOIN SeasonStandings ss ON t.team_id = ss.team_id 
                    AND ss.season_id = :season_id 
                    AND ss.round = :round
                LEFT JOIN Stadiums s ON t.home_stadium_id = s.stadium_id
                WHERE ss.position IS NOT NULL OR EXISTS (
                    SELECT 1 FROM TeamRosters tr 
                    WHERE tr.team_id = t.team_id AND tr.season_id = :season_id
                )
                ORDER BY COALESCE(ss.position, 999), t.name
            ''')
            
            result = db.session.execute(query, {
                'season_id': season_id,
                'round': latest_round
            })
            
            teams = []
            for row in result:
                team_dict = dict(row._mapping)
                
                # Xử lý stadium info
                stadium_info = {}
                if team_dict.get('home_stadium_id'):
                    stadium_info = {
                        'stadium_id': team_dict['home_stadium_id'],
                        'name': team_dict.get('stadium_name'),
                        'city': team_dict.get('stadium_city'),
                        'address': team_dict.get('stadium_address')
                    }
                
                # Xử lý standing info
                standing_info = {}
                if team_dict.get('position') is not None:
                    standing_info = {
                        'position': team_dict['position'],
                        'played': team_dict['played'],
                        'wins': team_dict['wins'],
                        'draws': team_dict['draws'],
                        'losses': team_dict['losses'],
                        'goals_for': team_dict['goals_for'],
                        'goals_against': team_dict['goals_against'],
                        'goal_difference': team_dict['goal_difference'],
                        'points': team_dict['points']
                    }
                
                # Tạo object kết quả
                result_obj = {
                    'team_id': team_dict['team_id'],
                    'name': team_dict['name'],
                    'logo_url': team_dict['logo_url'],
                    'home_stadium_id': team_dict['home_stadium_id'],
                    'home_stadium': stadium_info if stadium_info else None,
                    'standing': standing_info if standing_info else None
                }
                
                teams.append(result_obj)
            
            return teams
            
        except Exception as e:
            print(f"ERROR in get_teams_by_season: {str(e)}")
            return []
    
    @staticmethod
    def get_team_season_details(team_id, season_id):
        """Lấy thông tin chi tiết của đội trong mùa (bao gồm players)"""
        try:
            # Lấy thông tin đội cơ bản
            team = TeamService.get_team_by_id(team_id, include_stadium=True)
            if not team:
                return None
            
            # Lấy standing của đội trong mùa (vòng mới nhất)
            standing_query = text('''
                SELECT * FROM SeasonStandings 
                WHERE team_id = :team_id 
                AND season_id = :season_id
                ORDER BY round DESC 
                LIMIT 1
            ''')
            standing_result = db.session.execute(standing_query, {
                'team_id': team_id,
                'season_id': season_id
            }).fetchone()
            
            if standing_result:
                team['standing'] = dict(standing_result._mapping)
                # Chuyển đổi numeric thành float
                for key in team['standing']:
                    if hasattr(team['standing'][key], '__float__'):
                        team['standing'][key] = float(team['standing'][key])
            
            # Lấy danh sách cầu thủ trong mùa
            players_query = text('''
                SELECT 
                    tr.roster_id,
                    tr.shirt_number,
                    p.player_id,
                    p.full_name,
                    p.birth_date,
                    p.height_cm,
                    p.weight_kg,
                    p.position,
                    p.image_url
                FROM TeamRosters tr
                JOIN Players p ON tr.player_id = p.player_id
                WHERE tr.team_id = :team_id 
                AND tr.season_id = :season_id
                ORDER BY 
                    CASE 
                        WHEN tr.shirt_number IS NULL THEN 999
                        ELSE tr.shirt_number
                    END,
                    p.full_name
            ''')
            
            players_result = db.session.execute(players_query, {
                'team_id': team_id,
                'season_id': season_id
            })
            
            players = []
            for row in players_result:
                player_dict = dict(row._mapping)
                
                # Chuyển đổi birth_date
                birth_date_str = None
                if player_dict['birth_date']:
                    if hasattr(player_dict['birth_date'], 'isoformat'):
                        birth_date_str = player_dict['birth_date'].isoformat()
                    elif isinstance(player_dict['birth_date'], str):
                        birth_date_str = player_dict['birth_date']
                
                player_info = {
                    'player_id': player_dict['player_id'],
                    'full_name': player_dict['full_name'],
                    'birth_date': birth_date_str,
                    'height_cm': player_dict['height_cm'],
                    'weight_kg': player_dict['weight_kg'],
                    'position': player_dict['position'],
                    'image_url': player_dict['image_url']
                }
                
                roster_info = {
                    'roster_id': player_dict['roster_id'],
                    'shirt_number': player_dict['shirt_number'],
                    'player': player_info
                }
                players.append(roster_info)
            
            team['players'] = players
            return team
            
        except Exception as e:
            print(f"ERROR in get_team_season_details: {str(e)}")
            return None
    
    @staticmethod
    def get_team_statistics(team_id, season_id=None):
        """Lấy thống kê của đội (tổng hợp)"""
        try:
            # Query cơ bản để lấy số trận, thắng, hòa, thua
            stats_query = text('''
                SELECT 
                    COUNT(*) as total_matches,
                    SUM(CASE 
                        WHEN (home_team_id = :team_id AND home_score > away_score) 
                          OR (away_team_id = :team_id AND away_score > home_score) 
                        THEN 1 ELSE 0 
                    END) as wins,
                    SUM(CASE 
                        WHEN home_score = away_score 
                        THEN 1 ELSE 0 
                    END) as draws,
                    SUM(CASE 
                        WHEN (home_team_id = :team_id AND home_score < away_score) 
                          OR (away_team_id = :team_id AND away_score < home_score) 
                        THEN 1 ELSE 0 
                    END) as losses,
                    SUM(CASE 
                        WHEN home_team_id = :team_id THEN home_score
                        ELSE away_score 
                    END) as goals_for,
                    SUM(CASE 
                        WHEN home_team_id = :team_id THEN away_score
                        ELSE home_score 
                    END) as goals_against
                FROM Matches
                WHERE (home_team_id = :team_id OR away_team_id = :team_id)
                AND status = 'FT'
            ''')
            
            params = {'team_id': team_id}
            if season_id:
                stats_query = text('''
                    SELECT 
                        COUNT(*) as total_matches,
                        SUM(CASE 
                            WHEN (home_team_id = :team_id AND home_score > away_score) 
                              OR (away_team_id = :team_id AND away_score > home_score) 
                            THEN 1 ELSE 0 
                        END) as wins,
                        SUM(CASE 
                            WHEN home_score = away_score 
                            THEN 1 ELSE 0 
                        END) as draws,
                        SUM(CASE 
                            WHEN (home_team_id = :team_id AND home_score < away_score) 
                              OR (away_team_id = :team_id AND away_score < home_score) 
                            THEN 1 ELSE 0 
                        END) as losses,
                        SUM(CASE 
                            WHEN home_team_id = :team_id THEN home_score
                            ELSE away_score 
                        END) as goals_for,
                        SUM(CASE 
                            WHEN home_team_id = :team_id THEN away_score
                            ELSE home_score 
                        END) as goals_against
                    FROM Matches
                    WHERE (home_team_id = :team_id OR away_team_id = :team_id)
                    AND season_id = :season_id
                    AND status = 'FT'
                ''')
                params['season_id'] = season_id
            
            result = db.session.execute(stats_query, params).fetchone()
            
            if result:
                stats = dict(result._mapping)
                # Tính goal difference
                stats['goal_difference'] = (stats['goals_for'] or 0) - (stats['goals_against'] or 0)
                # Tính điểm
                stats['points'] = ((stats['wins'] or 0) * 3) + (stats['draws'] or 0)
                return stats
            
            return None
            
        except Exception as e:
            print(f"ERROR in get_team_statistics: {str(e)}")
            return None
        