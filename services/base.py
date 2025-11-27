from extensions import db
from sqlalchemy.exc import SQLAlchemyError

class BaseService:
    def save(self, obj):
        """Thêm mới hoặc cập nhật một đối tượng"""
        try:
            db.session.add(obj)
            db.session.commit()
            return True, obj
        except SQLAlchemyError as e:
            db.session.rollback()
            return False, str(e)

    def save_all(self, objects: list):
        """Lưu danh sách nhiều đối tượng cùng lúc"""
        try:
            db.session.add_all(objects)
            db.session.commit()
            return True, len(objects)
        except SQLAlchemyError as e:
            db.session.rollback()
            return False, str(e)

    def delete(self, obj):
        """Xóa đối tượng"""
        try:
            db.session.delete(obj)
            db.session.commit()
            return True, "Deleted"
        except SQLAlchemyError as e:
            db.session.rollback()
            return False, str(e)