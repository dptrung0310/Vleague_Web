# config.py
import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'football-social-network-secret-key')
    db_path = os.path.join(BASE_DIR, 'vleague.db').replace('\\', '/')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-for-football-app')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)  # Token hết hạn sau 7 ngày
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)  # Refresh token hết hạn sau 30 ngày
    
    # Bcrypt
    BCRYPT_LOG_ROUNDS = 12
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

current_config = DevelopmentConfig