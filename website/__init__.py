from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

#create db object
db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'TEST_KEY_CHANGE_THIS_LATER'
    app.url_map.strict_slashes = False

    # configure app database location
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'

    # weird SQL stuff
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # initialize app database
    db.init_app(app)

    from .views import views
    from .auth import auth
    from .pse import pse

    # flask blueprints registration
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(pse, url_prefix='/')

    # database
    from .models import Customer, Lot, Ticket, User

    # create database db
    create_database(app)

    # flask-login magic idk
    login_manager = LoginManager()
    login_manager.login_view = 'auth.admin_login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

# creates db for first time
def create_database(app):
    if not path.exists('instance/' + DB_NAME):
        with app.app_context():
            db.create_all()
        print(' --- Database Created ---')

