"""
Инициализация серверного приложения SysMonitor.

Модуль содержит фабричную функцию create_app(), которая настраивает
Flask-приложение, подключает базу данных, регистрирует blueprint с маршрутами
и выполняет создание таблиц в базе данных.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Глобальный объект базы данных, используемый всеми моделями приложения
db = SQLAlchemy()

def create_app():
    """
    Создать и сконфигурировать экземпляр Flask-приложения SysMonitor.

    Настраивает секретный ключ, подключение к базе данных SQLite, включает
    автообновление шаблонов, инициализирует SQLAlchemy и регистрирует blueprint
    с маршрутами пользовательского интерфейса.

    :return: сконфигурированное Flask-приложение.
    :rtype: flask.Flask
    """
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
