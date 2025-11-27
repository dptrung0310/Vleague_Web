from models.system_models.article import Article
from services.base import BaseService


class ArticleService(BaseService):
    def get_all_articles(self):
        # Có thể thêm logic phân trang hoặc sort theo created_at giảm dần ở đây
        articles = Article.query.order_by(Article.created_at.desc()).all()
        return [a.to_dict() for a in articles], 200

    def get_article_by_id(self, article_id):
        article = Article.query.get(article_id)
        if not article:
            return {'message': 'Không tìm thấy bài viết.'}, 404
        return article.to_dict(), 200

    def get_article_by_slug(self, slug):
        """Hỗ trợ lấy bài viết theo URL thân thiện"""
        article = Article.query.filter_by(slug=slug).first()
        if not article:
            return {'message': 'Không tìm thấy bài viết.'}, 404
        return article.to_dict(), 200

    def create_article(self, data):
        # Kiểm tra trùng slug nếu có
        if data.get('slug') and Article.query.filter_by(slug=data['slug']).first():
            return {'message': 'Slug (đường dẫn) đã tồn tại.'}, 409

        new_article = Article(
            title=data['title'],
            slug=data.get('slug'),  # Nên có logic tạo slug tự động từ title nếu null
            content=data['content'],
            thumbnail_url=data.get('thumbnail_url'),
            author_id=data.get('author_id'),
            related_match_id=data.get('related_match_id')
        )

        success, result = self.save(new_article)
        if success:
            return {'message': 'Đăng bài thành công', 'article': result.to_dict()}, 201
        return {'message': f'Lỗi DB: {result}'}, 500

    def update_article(self, article_id, data):
        article = Article.query.get(article_id)
        if not article:
            return {'message': 'Không tìm thấy bài viết.'}, 404

        article.title = data.get('title', article.title)
        article.content = data.get('content', article.content)
        article.thumbnail_url = data.get('thumbnail_url', article.thumbnail_url)
        article.related_match_id = data.get('related_match_id', article.related_match_id)

        # Nếu đổi slug, cần check trùng
        if 'slug' in data and data['slug'] != article.slug:
            if Article.query.filter_by(slug=data['slug']).first():
                return {'message': 'Slug đã tồn tại.'}, 409
            article.slug = data['slug']

        success, result = self.save(article)
        if success:
            return {'message': 'Cập nhật thành công', 'article': result.to_dict()}, 200
        return {'message': f'Lỗi cập nhật: {result}'}, 500

    def delete_article(self, article_id):
        article = Article.query.get(article_id)
        if not article:
            return {'message': 'Không tìm thấy bài viết.'}, 404

        success, result = self.delete(article)
        if success:
            return {'message': 'Xóa bài viết thành công.'}, 200
        return {'message': f'Lỗi xóa: {result}'}, 500