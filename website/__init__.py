from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .extensions import socketio
import json

db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    with open('chatapp/config.json', 'r') as config_file:
            config = json.load(config_file)
    app.config['SECRET_KEY'] = config['SECRET_KEY']
    app.config['UPLOAD_FOLDER'] = config['UPLOAD_FOLDER']
    app.config['SQLALCHEMY_DATABASE_URI'] = config['SQLALCHEMY_DATABASE_URI']
    db.init_app(app)
    
    with app.app_context():
        from .models import User, Message, Room
        from .views import views
        from .auth import auth
        from .functions import get_admins

        app.register_blueprint(views, url_prefix='/')
        app.register_blueprint(auth, url_prefix='/')

        socketio.init_app(app)

        login_manager = LoginManager()
        login_manager.login_view = 'auth.login'
        login_manager.init_app(app)

        @login_manager.user_loader
        def load_user(id):
            return User.query.get(str(id))

        db.create_all()
        
    return app