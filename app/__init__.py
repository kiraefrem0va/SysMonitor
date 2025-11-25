from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'kira-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sysmonitor.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Автообновление шаблонов Jinja2
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.jinja_env.auto_reload = True

    db.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()

    return app
