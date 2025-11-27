from flask import request
from flask_restx import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import cache
from services.system_services.article_service import ArticleService


def init_article_routes(api, namespace, schemas):
    service = ArticleService()

    output_model = schemas['article_output']
    input_model = schemas['article_input']

    @namespace.route('')
    class ArticleList(Resource):
        @namespace.doc('list_articles')
        @namespace.marshal_list_with(output_model)
        @cache.cached(timeout=60, key_prefix='all_articles')
        def get(self):
            """Lấy danh sách bài viết mới nhất"""
            return service.get_all_articles()

        @namespace.doc('create_article', security='jwt')
        @namespace.expect(input_model, validate=True)
        @jwt_required()
        def post(self):
            """Đăng bài viết mới"""
            data = request.json
            # Tự động lấy ID người đăng từ token
            current_user_id = get_jwt_identity()
            # Nếu data chưa có author_id thì gán user hiện tại
            if 'author_id' not in data:
                data['author_id'] = current_user_id

            cache.delete('all_articles')
            return service.create_article(data)

    @namespace.route('/<int:id>')
    @namespace.param('id', 'Article ID')
    class ArticleResource(Resource):
        @namespace.doc('get_article')
        @namespace.marshal_with(output_model)
        @cache.cached(timeout=300)
        def get(self, id):
            """Xem chi tiết bài viết theo ID"""
            return service.get_article_by_id(id)

        @namespace.doc('update_article', security='jwt')
        @namespace.expect(input_model)
        @jwt_required()
        def put(self, id):
            """Cập nhật bài viết"""
            cache.delete('all_articles')
            # Nên thêm logic check xem user hiện tại có phải tác giả hoặc admin không
            return service.update_article(id, request.json)

        @namespace.doc('delete_article', security='jwt')
        @jwt_required()
        def delete(self, id):
            """Xóa bài viết"""
            cache.delete('all_articles')
            return service.delete_article(id)

    @namespace.route('/slug/<string:slug>')
    @namespace.param('slug', 'Article URL Slug')
    class ArticleBySlug(Resource):
        @namespace.doc('get_article_by_slug')
        @namespace.marshal_with(output_model)
        @cache.cached(timeout=300)
        def get(self, slug):
            """Xem chi tiết bài viết theo Slug (URL thân thiện)"""
            return service.get_article_by_slug(slug)