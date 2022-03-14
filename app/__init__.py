from flask import Flask
from flask_cors import CORS
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
bootstrap = Bootstrap()
login = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__, static_folder='static/')
    app.config.from_object(config_class)
    app.jinja_env.auto_reload = True

    # load apps 
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
    bootstrap.init_app(app)
    login.init_app(app)

    # create db
    with app.app_context():
        db.create_all()

    # load blueprints
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app

from app import models

