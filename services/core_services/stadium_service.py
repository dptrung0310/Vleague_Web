from models.core_models.stadium import Stadium
from services.base import BaseService

class StadiumService(BaseService):
    def get_all_stadiums(self):
        stadiums = Stadium.query.all()
        return [s.to_dict() for s in stadiums], 200

    def get_stadium_by_id(self, stadium_id):
        stadium = Stadium.query.get(stadium_id)
        if not stadium:
            return {'message': 'Không tìm thấy sân vận động.'}, 404
        return stadium.to_dict(), 200

    def create_stadium(self, data):
        new_stadium = Stadium(
            name=data['name'],
            city=data['city'],
            address=data.get('address'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude')
        )

        success, result = self.save(new_stadium)
        if success:
            return {'message': 'Thêm sân thành công', 'stadium': result.to_dict()}, 201
        return {'message': f'Lỗi DB: {result}'}, 500

    def update_stadium(self, stadium_id, data):
        stadium = Stadium.query.get(stadium_id)
        if not stadium:
            return {'message': 'Không tìm thấy sân vận động.'}, 404

        stadium.name = data.get('name', stadium.name)
        stadium.city = data.get('city', stadium.city)
        stadium.address = data.get('address', stadium.address)
        stadium.latitude = data.get('latitude', stadium.latitude)
        stadium.longitude = data.get('longitude', stadium.longitude)

        success, result = self.save(stadium)
        if success:
            return {'message': 'Cập nhật thành công', 'stadium': result.to_dict()}, 200
        return {'message': f'Lỗi cập nhật: {result}'}, 500

    def delete_stadium(self, stadium_id):
        stadium = Stadium.query.get(stadium_id)
        if not stadium:
            return {'message': 'Không tìm thấy sân vận động.'}, 404

        success, result = self.delete(stadium)
        if success:
            return {'message': 'Xóa sân thành công.'}, 200
        return {'message': f'Lỗi xóa: {result}'}, 500