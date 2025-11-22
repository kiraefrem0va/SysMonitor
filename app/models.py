from . import db
from datetime import datetime

class Computer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(128), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    metrics = db.relationship('Metric', backref='computer', lazy=True, cascade="all, delete-orphan")

class Metric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    computer_id = db.Column(db.Integer, db.ForeignKey('computer.id'), nullable=False)
    cpu_percent = db.Column(db.Float)
    memory_usage = db.Column(db.Float)
    disk_usage = db.Column(db.Float)
    processes = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
