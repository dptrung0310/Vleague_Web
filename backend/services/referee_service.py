from extensions import db
from sqlalchemy import text

class RefereeService:
    @staticmethod
    def get_all_referees():
        try:
            query = text('SELECT * FROM Referees ORDER BY full_name')
            result = db.session.execute(query)
            
            return [dict(row._mapping) for row in result]
            
        except Exception as e:
            print(f"ERROR in get_all_referees: {str(e)}")
            return []
    
    @staticmethod
    def get_referee_by_id(referee_id):
        try:
            query = text('SELECT * FROM Referees WHERE referee_id = :id')
            result = db.session.execute(query, {'id': referee_id}).fetchone()
            
            return dict(result._mapping) if result else None
            
        except Exception as e:
            print(f"ERROR in get_referee_by_id: {str(e)}")
            return None
    
    @staticmethod
    def create_referee(data):
        try:
            query = text('''
                INSERT INTO Referees (full_name)
                VALUES (:full_name)
            ''')
            
            db.session.execute(query, data)
            db.session.commit()
            
            # Lấy ID vừa tạo
            last_id = db.session.execute(text('SELECT last_insert_rowid()')).fetchone()[0]
            
            return RefereeService.get_referee_by_id(last_id)
            
        except Exception as e:
            print(f"ERROR in create_referee: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def update_referee(referee_id, data):
        try:
            existing = RefereeService.get_referee_by_id(referee_id)
            if not existing:
                return None
            
            query = text('''
                UPDATE Referees 
                SET full_name = :full_name
                WHERE referee_id = :referee_id
            ''')
            
            params = data.copy()
            params['referee_id'] = referee_id
            
            db.session.execute(query, params)
            db.session.commit()
            
            return RefereeService.get_referee_by_id(referee_id)
            
        except Exception as e:
            print(f"ERROR in update_referee: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def delete_referee(referee_id):
        try:
            existing = RefereeService.get_referee_by_id(referee_id)
            if not existing:
                return False
            
            query = text('DELETE FROM Referees WHERE referee_id = :referee_id')
            db.session.execute(query, {'referee_id': referee_id})
            db.session.commit()
            
            return True
            
        except Exception as e:
            print(f"ERROR in delete_referee: {str(e)}")
            db.session.rollback()
            return False