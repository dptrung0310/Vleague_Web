import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Cho phép OAuth chạy trên HTTP (chỉ dùng cho môi trường dev/local)
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///vleague.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT
    JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=1)

    # OAuth Config
    # Key này dùng để mã hóa session cho quy trình login Google
    SECRET_KEY = os.getenv('SECRET_KEY', 'mot-chuoi-bi-mat-rat-dai-va-ngau-nhien')
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

    # Cache
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300

    # Swagger Authorization
    AUTHORIZATIONS = {
        'jwt': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': "Type in the *'Value'* input field: **Bearer <JWT>**, where JWT is the access token"
        }
    }
