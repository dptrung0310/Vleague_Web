from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth

db = SQLAlchemy()
jwt = JWTManager()
cache = Cache()
bcrypt = Bcrypt()
oauth = OAuth()