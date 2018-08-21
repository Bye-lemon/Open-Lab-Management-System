from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

login_manager = LoginManager()
mail = Mail()
db = SQLAlchemy()

login_manager.login_view = 'auth.login'


def create_app():
    app = Flask(__name__)
    

    login_manager.init_app(app)
    mail.init_app(app)
    db.init_app(app)

    return app
