from extensions import db
from sqlalchemy import text
from datetime import datetime

class PlayerService:
    @staticmethod
    def get_all_players():
        try:
            query = text('SELECT * FROM Players ORDER BY full_name')
            result = db.session.execute(query)
            
            players = []
            for row in result:
                player_dict = dict(row._mapping)
                # Xử lý birth_date
                if player_dict.get('birth_date'):
                    if isinstance(player_dict['birth_date'], str):
                        try:
                            player_dict['birth_date'] = datetime.strptime(
                                player_dict['birth_date'], '%Y-%m-%d'
                            ).date().isoformat()
                        except:
                            player_dict['birth_date'] = None
                    elif hasattr(player_dict['birth_date'], 'isoformat'):
                        player_dict['birth_date'] = player_dict['birth_date'].isoformat()
                
                players.append(player_dict)
            
            return players
            
        except Exception as e:
            print(f"ERROR in get_all_players: {str(e)}")
            db.session.rollback()
            return []
    
    @staticmethod
    def get_player_by_id(player_id):
        try:
            query = text('SELECT * FROM Players WHERE player_id = :id')
            result = db.session.execute(query, {'id': player_id}).fetchone()
            
            if result:
                player_dict = dict(result._mapping)
                # Xử lý birth_date
                if player_dict.get('birth_date'):
                    if isinstance(player_dict['birth_date'], str):
                        try:
                            player_dict['birth_date'] = datetime.strptime(
                                player_dict['birth_date'], '%Y-%m-%d'
                            ).date().isoformat()
                        except:
                            player_dict['birth_date'] = None
                    elif hasattr(player_dict['birth_date'], 'isoformat'):
                        player_dict['birth_date'] = player_dict['birth_date'].isoformat()
                
                return player_dict
            return None
            
        except Exception as e:
            print(f"ERROR in get_player_by_id: {str(e)}")
            return None
    
    @staticmethod
    def create_player(data):
        try:
            # Parse birth_date nếu là string
            if 'birth_date' in data and isinstance(data['birth_date'], str):
                try:
                    data['birth_date'] = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
                except:
                    data['birth_date'] = None
            
            columns = []
            values = []
            params = {}
            
            for key, value in data.items():
                columns.append(key)
                values.append(f":{key}")
                params[key] = value
            
            query = text(f'''
                INSERT INTO Players ({', '.join(columns)})
                VALUES ({', '.join(values)})
            ''')
            
            db.session.execute(query, params)
            db.session.commit()
            
            # Lấy ID vừa tạo
            last_id = db.session.execute(text('SELECT last_insert_rowid()')).fetchone()[0]
            
            return PlayerService.get_player_by_id(last_id)
            
        except Exception as e:
            print(f"ERROR in create_player: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def update_player(player_id, data):
        try:
            existing = PlayerService.get_player_by_id(player_id)
            if not existing:
                return None
            
            # Parse birth_date nếu là string
            if 'birth_date' in data and isinstance(data['birth_date'], str):
                try:
                    data['birth_date'] = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
                except:
                    data['birth_date'] = None
            
            set_clause = ', '.join([f"{key} = :{key}" for key in data.keys()])
            query = text(f'''
                UPDATE Players 
                SET {set_clause}
                WHERE player_id = :player_id
            ''')
            
            params = data.copy()
            params['player_id'] = player_id
            
            db.session.execute(query, params)
            db.session.commit()
            
            return PlayerService.get_player_by_id(player_id)
            
        except Exception as e:
            print(f"ERROR in update_player: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def delete_player(player_id):
        try:
            existing = PlayerService.get_player_by_id(player_id)
            if not existing:
                return False
            
            query = text('DELETE FROM Players WHERE player_id = :player_id')
            db.session.execute(query, {'player_id': player_id})
            db.session.commit()
            
            return True
            
        except Exception as e:
            print(f"ERROR in delete_player: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def search_players(name=None, position=None):
        try:
            query = 'SELECT * FROM Players WHERE 1=1'
            params = {}
            
            if name:
                query += ' AND full_name LIKE :name'
                params['name'] = f'%{name}%'
            
            if position:
                query += ' AND position = :position'
                params['position'] = position
            
            query += ' ORDER BY full_name'
            
            result = db.session.execute(text(query), params)
            
            players = []
            for row in result:
                player_dict = dict(row._mapping)
                if player_dict.get('birth_date'):
                    if isinstance(player_dict['birth_date'], str):
                        try:
                            player_dict['birth_date'] = datetime.strptime(
                                player_dict['birth_date'], '%Y-%m-%d'
                            ).date().isoformat()
                        except:
                            player_dict['birth_date'] = None
                    elif hasattr(player_dict['birth_date'], 'isoformat'):
                        player_dict['birth_date'] = player_dict['birth_date'].isoformat()
                
                players.append(player_dict)
            
            return players
            
        except Exception as e:
            print(f"ERROR in search_players: {str(e)}")
            return []