from . import db
from datetime import datetime

class Computer(db.Model):
    """
    Модель компьютера, зарегистрированного в системе SysMonitor.

    Хранит базовую информацию о рабочей станции и связь с измерениями метрик.
    """
    id = db.Column(db.Integer, primary_key=True) # уникальный идентификатор компьютера
    hostname = db.Column(db.String(128), unique=True, nullable=False) # уникальный идентификатор компьютера
    created_at = db.Column(db.DateTime, default=datetime.utcnow) # дата и время регистрации компьютера в системе

    metrics = db.relationship('Metric', backref='computer', lazy=True, cascade="all, delete-orphan") # список всех измерений (Metric), связанных с данным компьютером

class Metric(db.Model):
    """
    Модель отдельного измерения системных метрик.

    Каждая запись соответствует одному «снимку» состояния компьютера в определённый момент времени.
    """
    id = db.Column(db.Integer, primary_key=True) # идентификатор измерения
    computer_id = db.Column(db.Integer, db.ForeignKey('computer.id'), nullable=False) # ссылка на таблицу Computer
    cpu_percent = db.Column(db.Float) # загрузка CPU, %
    memory_usage = db.Column(db.Float) # использование RAM, %
    disk_usage = db.Column(db.Float) # заполненность диска, %
    processes = db.Column(db.Integer)  # количество запущенных процессов
    timestamp = db.Column(db.DateTime, default=datetime.utcnow) # отметка времени, когда были сняты метрики
