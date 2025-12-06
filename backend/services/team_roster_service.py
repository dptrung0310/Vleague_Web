from extensions import db
from sqlalchemy import text

class TeamRosterService:
    @staticmethod
    def get_all_rosters():
        try:
            query = text('SELECT * FROM TeamRosters ORDER BY season_id, team_id')
            result = db.session.execute(query)
            
            return [dict(row._mapping) for row in result]
        except Exception as e:
            print(f"ERROR in get_all_rosters: {str(e)}")
            return []
    
    @staticmethod
    def get_roster_by_id(roster_id):
        try:
            query = text('SELECT * FROM TeamRosters WHERE roster_id = :id')
            result = db.session.execute(query, {'id': roster_id}).fetchone()
            
            return dict(result._mapping) if result else None
        except Exception as e:
            print(f"ERROR in get_roster_by_id: {str(e)}")
            return None
    
    @staticmethod
    def create_roster(data):
        try:
            columns = []
            values = []
            params = {}
            
            for key, value in data.items():
                columns.append(key)
                values.append(f":{key}")
                params[key] = value
            
            query = text(f'''
                INSERT INTO TeamRosters ({', '.join(columns)})
                VALUES ({', '.join(values)})
            ''')
            
            db.session.execute(query, params)
            db.session.commit()
            
            # Lấy ID vừa tạo
            last_id = db.session.execute(text('SELECT last_insert_rowid()')).fetchone()[0]
            
            return TeamRosterService.get_roster_by_id(last_id)
        except Exception as e:
            print(f"ERROR in create_roster: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def update_roster(roster_id, data):
        try:
            existing = TeamRosterService.get_roster_by_id(roster_id)
            if not existing:
                return None
            
            set_clause = ', '.join([f"{key} = :{key}" for key in data.keys()])
            query = text(f'''
                UPDATE TeamRosters 
                SET {set_clause}
                WHERE roster_id = :roster_id
            ''')
            
            params = data.copy()
            params['roster_id'] = roster_id
            
            db.session.execute(query, params)
            db.session.commit()
            
            return TeamRosterService.get_roster_by_id(roster_id)
        except Exception as e:
            print(f"ERROR in update_roster: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def delete_roster(roster_id):
        try:
            existing = TeamRosterService.get_roster_by_id(roster_id)
            if not existing:
                return False
            
            query = text('DELETE FROM TeamRosters WHERE roster_id = :roster_id')
            db.session.execute(query, {'roster_id': roster_id})
            db.session.commit()
            
            return True
        except Exception as e:
            print(f"ERROR in delete_roster: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def get_rosters_by_team(team_id, season_id=None):
        try:
            if season_id:
                query = text('''
                    SELECT * FROM TeamRosters 
                    WHERE team_id = :team_id AND season_id = :season_id
                    ORDER BY shirt_number
                ''')
                params = {'team_id': team_id, 'season_id': season_id}
            else:
                query = text('''
                    SELECT * FROM TeamRosters 
                    WHERE team_id = :team_id
                    ORDER BY season_id, shirt_number
                ''')
                params = {'team_id': team_id}
            
            result = db.session.execute(query, params)
            
            return [dict(row._mapping) for row in result]
        except Exception as e:
            print(f"ERROR in get_rosters_by_team: {str(e)}")
            return []
    
    @staticmethod
    def get_rosters_by_player(player_id):
        try:
            query = text('''
                SELECT * FROM TeamRosters 
                WHERE player_id = :player_id
                ORDER BY season_id
            ''')
            result = db.session.execute(query, {'player_id': player_id})
            
            return [dict(row._mapping) for row in result]
        except Exception as e:
            print(f"ERROR in get_rosters_by_player: {str(e)}")
            return []
    
    @staticmethod
    def get_rosters_by_season(season_id):
        try:
            query = text('''
                SELECT tr.*, t.name as team_name, p.full_name as player_name
                FROM TeamRosters tr
                LEFT JOIN Teams t ON tr.team_id = t.team_id
                LEFT JOIN Players p ON tr.player_id = p.player_id
                WHERE tr.season_id = :season_id
                ORDER BY t.name, tr.shirt_number
            ''')
            result = db.session.execute(query, {'season_id': season_id})
            
            rosters = []
            for row in result:
                roster_dict = dict(row._mapping)
                rosters.append(roster_dict)
            
            return rosters
        except Exception as e:
            print(f"ERROR in get_rosters_by_season: {str(e)}")
            return []