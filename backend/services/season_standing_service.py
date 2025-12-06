from extensions import db
from sqlalchemy import text

class SeasonStandingService:
    @staticmethod
    def get_all_standings():
        try:
            query = text('SELECT * FROM SeasonStandings ORDER BY season_id, round, position')
            result = db.session.execute(query)
            
            return [dict(row._mapping) for row in result]
        except Exception as e:
            print(f"ERROR in get_all_standings: {str(e)}")
            return []
    
    @staticmethod
    def get_standing_by_id(standing_id):
        try:
            query = text('SELECT * FROM SeasonStandings WHERE standing_id = :id')
            result = db.session.execute(query, {'id': standing_id}).fetchone()
            
            return dict(result._mapping) if result else None
        except Exception as e:
            print(f"ERROR in get_standing_by_id: {str(e)}")
            return None
    
    @staticmethod
    def create_standing(data):
        try:
            columns = []
            values = []
            params = {}
            
            for key, value in data.items():
                columns.append(key)
                values.append(f":{key}")
                params[key] = value
            
            query = text(f'''
                INSERT INTO SeasonStandings ({', '.join(columns)})
                VALUES ({', '.join(values)})
            ''')
            
            db.session.execute(query, params)
            db.session.commit()
            
            # Lấy ID vừa tạo
            last_id = db.session.execute(text('SELECT last_insert_rowid()')).fetchone()[0]
            
            return SeasonStandingService.get_standing_by_id(last_id)
        except Exception as e:
            print(f"ERROR in create_standing: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def update_standing(standing_id, data):
        try:
            existing = SeasonStandingService.get_standing_by_id(standing_id)
            if not existing:
                return None
            
            set_clause = ', '.join([f"{key} = :{key}" for key in data.keys()])
            query = text(f'''
                UPDATE SeasonStandings 
                SET {set_clause}
                WHERE standing_id = :standing_id
            ''')
            
            params = data.copy()
            params['standing_id'] = standing_id
            
            db.session.execute(query, params)
            db.session.commit()
            
            return SeasonStandingService.get_standing_by_id(standing_id)
        except Exception as e:
            print(f"ERROR in update_standing: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def delete_standing(standing_id):
        try:
            existing = SeasonStandingService.get_standing_by_id(standing_id)
            if not existing:
                return False
            
            query = text('DELETE FROM SeasonStandings WHERE standing_id = :standing_id')
            db.session.execute(query, {'standing_id': standing_id})
            db.session.commit()
            
            return True
        except Exception as e:
            print(f"ERROR in delete_standing: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def get_standings_by_season(season_id, round=None):
        try:
            if round:
                query = text('''
                    SELECT ss.*, t.name as team_name, t.logo_url
                    FROM SeasonStandings ss
                    LEFT JOIN Teams t ON ss.team_id = t.team_id
                    WHERE ss.season_id = :season_id AND ss.round = :round
                    ORDER BY ss.position
                ''')
                params = {'season_id': season_id, 'round': round}
            else:
                query = text('''
                    SELECT ss.*, t.name as team_name, t.logo_url
                    FROM SeasonStandings ss
                    LEFT JOIN Teams t ON ss.team_id = t.team_id
                    WHERE ss.season_id = :season_id
                    ORDER BY ss.round, ss.position
                ''')
                params = {'season_id': season_id}
            
            result = db.session.execute(query, params)
            
            standings = []
            for row in result:
                standing_dict = dict(row._mapping)
                standings.append(standing_dict)
            
            return standings
        except Exception as e:
            print(f"ERROR in get_standings_by_season: {str(e)}")
            return []
    
    @staticmethod
    def get_standings_by_team(team_id):
        try:
            query = text('''
                SELECT ss.*, s.name as season_name
                FROM SeasonStandings ss
                LEFT JOIN Seasons s ON ss.season_id = s.season_id
                WHERE ss.team_id = :team_id
                ORDER BY ss.season_id, ss.round
            ''')
            result = db.session.execute(query, {'team_id': team_id})
            
            return [dict(row._mapping) for row in result]
        except Exception as e:
            print(f"ERROR in get_standings_by_team: {str(e)}")
            return []
    
    @staticmethod
    def get_current_round_standings(season_id):
        try:
            # Lấy vòng đấu hiện tại (vòng lớn nhất) của mùa giải
            query = text('''
                SELECT MAX(round) as current_round
                FROM SeasonStandings 
                WHERE season_id = :season_id
            ''')
            result = db.session.execute(query, {'season_id': season_id}).fetchone()
            
            if result and result.current_round:
                return SeasonStandingService.get_standings_by_season(season_id, result.current_round)
            return []
        except Exception as e:
            print(f"ERROR in get_current_round_standings: {str(e)}")
            return []
    
    @staticmethod
    def get_standings_with_details(season_id, round):
        try:
            query = text('''
                SELECT ss.*, 
                       t.name as team_name,
                       t.logo_url,
                       s.name as season_name,
                       s.start_date as season_start,
                       s.end_date as season_end
                FROM SeasonStandings ss
                LEFT JOIN Teams t ON ss.team_id = t.team_id
                LEFT JOIN Seasons s ON ss.season_id = s.season_id
                WHERE ss.season_id = :season_id AND ss.round = :round
                ORDER BY ss.position
            ''')
            
            result = db.session.execute(query, {'season_id': season_id, 'round': round})
            
            standings = []
            for row in result:
                standing_dict = dict(row._mapping)
                standings.append(standing_dict)
            
            return standings
        except Exception as e:
            print(f"ERROR in get_standings_with_details: {str(e)}")
            return []