from extensions import db
from sqlalchemy import text

class StadiumService:
    @staticmethod
    def get_all_stadiums():
        try:
            query = text('SELECT * FROM Stadiums ORDER BY name')
            result = db.session.execute(query)
            
            stadiums = []
            for row in result:
                stadium_dict = dict(row._mapping)
                # Chuyển đổi Decimal sang float
                for coord in ['latitude', 'longitude']:
                    if stadium_dict.get(coord):
                        stadium_dict[coord] = float(stadium_dict[coord])
                
                stadiums.append(stadium_dict)
            
            return stadiums
            
        except Exception as e:
            print(f"ERROR in get_all_stadiums: {str(e)}")
            return []
    
    @staticmethod
    def get_stadium_by_id(stadium_id):
        try:
            query = text('SELECT * FROM Stadiums WHERE stadium_id = :id')
            result = db.session.execute(query, {'id': stadium_id}).fetchone()
            
            if result:
                stadium_dict = dict(result._mapping)
                # Chuyển đổi Decimal sang float
                for coord in ['latitude', 'longitude']:
                    if stadium_dict.get(coord):
                        stadium_dict[coord] = float(stadium_dict[coord])
                
                return stadium_dict
            return None
            
        except Exception as e:
            print(f"ERROR in get_stadium_by_id: {str(e)}")
            return None
    
    @staticmethod
    def create_stadium(data):
        try:
            columns = []
            values = []
            params = {}
            
            for key, value in data.items():
                columns.append(key)
                values.append(f":{key}")
                params[key] = value
            
            query = text(f'''
                INSERT INTO Stadiums ({', '.join(columns)})
                VALUES ({', '.join(values)})
            ''')
            
            db.session.execute(query, params)
            db.session.commit()
            
            # Lấy ID vừa tạo
            last_id = db.session.execute(text('SELECT last_insert_rowid()')).fetchone()[0]
            
            return StadiumService.get_stadium_by_id(last_id)
            
        except Exception as e:
            print(f"ERROR in create_stadium: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def update_stadium(stadium_id, data):
        try:
            existing = StadiumService.get_stadium_by_id(stadium_id)
            if not existing:
                return None
            
            set_clause = ', '.join([f"{key} = :{key}" for key in data.keys()])
            query = text(f'''
                UPDATE Stadiums 
                SET {set_clause}
                WHERE stadium_id = :stadium_id
            ''')
            
            params = data.copy()
            params['stadium_id'] = stadium_id
            
            db.session.execute(query, params)
            db.session.commit()
            
            return StadiumService.get_stadium_by_id(stadium_id)
            
        except Exception as e:
            print(f"ERROR in update_stadium: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def delete_stadium(stadium_id):
        try:
            existing = StadiumService.get_stadium_by_id(stadium_id)
            if not existing:
                return False
            
            query = text('DELETE FROM Stadiums WHERE stadium_id = :stadium_id')
            db.session.execute(query, {'stadium_id': stadium_id})
            db.session.commit()
            
            return True
            
        except Exception as e:
            print(f"ERROR in delete_stadium: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def get_stadiums_by_city(city):
        try:
            query = text('SELECT * FROM Stadiums WHERE city = :city ORDER BY name')
            result = db.session.execute(query, {'city': city})
            
            stadiums = []
            for row in result:
                stadium_dict = dict(row._mapping)
                for coord in ['latitude', 'longitude']:
                    if stadium_dict.get(coord):
                        stadium_dict[coord] = float(stadium_dict[coord])
                
                stadiums.append(stadium_dict)
            
            return stadiums
            
        except Exception as e:
            print(f"ERROR in get_stadiums_by_city: {str(e)}")
            return []