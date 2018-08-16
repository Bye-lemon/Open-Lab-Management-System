from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

login_manager = LoginManager()
db = SQLAlchemy()

def create_app():

    app = Flask(__name__)

    login_manager.init_app(app)
    db.init_app(app)

    return app