from extensions import db
from sqlalchemy import text
from datetime import datetime

class SeasonService:
    @staticmethod
    def get_all_seasons():
        try:
            query = text('SELECT * FROM Seasons ORDER BY start_date DESC')
            result = db.session.execute(query)
            
            seasons = []
            for row in result:
                season_dict = dict(row._mapping)
                # Xử lý date fields
                for date_field in ['start_date', 'end_date']:
                    if season_dict.get(date_field):
                        if isinstance(season_dict[date_field], str):
                            try:
                                season_dict[date_field] = datetime.strptime(
                                    season_dict[date_field], '%Y-%m-%d'
                                ).date().isoformat()
                            except:
                                season_dict[date_field] = None
                        elif hasattr(season_dict[date_field], 'isoformat'):
                            season_dict[date_field] = season_dict[date_field].isoformat()
                
                seasons.append(season_dict)
            
            return seasons
            
        except Exception as e:
            print(f"ERROR in get_all_seasons: {str(e)}")
            return []
    
    @staticmethod
    def get_season_by_id(season_id):
        try:
            query = text('SELECT * FROM Seasons WHERE season_id = :id')
            result = db.session.execute(query, {'id': season_id}).fetchone()
            
            if result:
                season_dict = dict(result._mapping)
                # Xử lý date fields
                for date_field in ['start_date', 'end_date']:
                    if season_dict.get(date_field):
                        if isinstance(season_dict[date_field], str):
                            try:
                                season_dict[date_field] = datetime.strptime(
                                    season_dict[date_field], '%Y-%m-%d'
                                ).date().isoformat()
                            except:
                                season_dict[date_field] = None
                        elif hasattr(season_dict[date_field], 'isoformat'):
                            season_dict[date_field] = season_dict[date_field].isoformat()
                
                return season_dict
            return None
            
        except Exception as e:
            print(f"ERROR in get_season_by_id: {str(e)}")
            return None
    
    @staticmethod
    def get_current_season():
        try:
            query = text('''
                SELECT * FROM Seasons 
                WHERE start_date <= DATE('now') 
                AND end_date >= DATE('now')
                ORDER BY start_date DESC
                LIMIT 1
            ''')
            result = db.session.execute(query).fetchone()
            
            if result:
                season_dict = dict(result._mapping)
                for date_field in ['start_date', 'end_date']:
                    if season_dict.get(date_field):
                        if isinstance(season_dict[date_field], str):
                            try:
                                season_dict[date_field] = datetime.strptime(
                                    season_dict[date_field], '%Y-%m-%d'
                                ).date().isoformat()
                            except:
                                season_dict[date_field] = None
                        elif hasattr(season_dict[date_field], 'isoformat'):
                            season_dict[date_field] = season_dict[date_field].isoformat()
                
                return season_dict
            return None
            
        except Exception as e:
            print(f"ERROR in get_current_season: {str(e)}")
            return None
    
    @staticmethod
    def create_season(data):
        try:
            # Parse date fields
            for date_field in ['start_date', 'end_date']:
                if date_field in data and isinstance(data[date_field], str):
                    try:
                        data[date_field] = datetime.strptime(data[date_field], '%Y-%m-%d').date()
                    except:
                        data[date_field] = None
            
            columns = []
            values = []
            params = {}
            
            for key, value in data.items():
                columns.append(key)
                values.append(f":{key}")
                params[key] = value
            
            query = text(f'''
                INSERT INTO Seasons ({', '.join(columns)})
                VALUES ({', '.join(values)})
            ''')
            
            db.session.execute(query, params)
            db.session.commit()
            
            return SeasonService.get_season_by_id(data['season_id'])
            
        except Exception as e:
            print(f"ERROR in create_season: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def update_season(season_id, data):
        try:
            existing = SeasonService.get_season_by_id(season_id)
            if not existing:
                return None
            
            # Parse date fields
            for date_field in ['start_date', 'end_date']:
                if date_field in data and isinstance(data[date_field], str):
                    try:
                        data[date_field] = datetime.strptime(data[date_field], '%Y-%m-%d').date()
                    except:
                        data[date_field] = None
            
            set_clause = ', '.join([f"{key} = :{key}" for key in data.keys()])
            query = text(f'''
                UPDATE Seasons 
                SET {set_clause}
                WHERE season_id = :season_id
            ''')
            
            params = data.copy()
            params['season_id'] = season_id
            
            db.session.execute(query, params)
            db.session.commit()
            
            return SeasonService.get_season_by_id(season_id)
            
        except Exception as e:
            print(f"ERROR in update_season: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def delete_season(season_id):
        try:
            existing = SeasonService.get_season_by_id(season_id)
            if not existing:
                return False
            
            query = text('DELETE FROM Seasons WHERE season_id = :season_id')
            db.session.execute(query, {'season_id': season_id})
            db.session.commit()
            
            return True
            
        except Exception as e:
            print(f"ERROR in delete_season: {str(e)}")
            db.session.rollback()
            return False