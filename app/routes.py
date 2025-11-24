from flask import Blueprint, render_template, request, jsonify
from .models import Computer, Metric
from . import db
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def index():
    from .models import Computer
    computers = Computer.query.all()
    return render_template('index.html', computers=computers)


@main.route('/api/metrics', methods=['POST'])
def receive_metrics():
    data = request.get_json()
    hostname = data.get('hostname')

    if not hostname:
        return jsonify({'error': 'hostname required'}), 400

    comp = Computer.query.filter_by(hostname=hostname).first()
    if not comp:
        comp = Computer(hostname=hostname)
        db.session.add(comp)
        db.session.commit()

    metric = Metric(
        computer_id=comp.id,
        cpu_percent=data.get('cpu_percent'),
        memory_usage=data.get('memory_usage'),
        disk_usage=data.get('disk_usage'),
        processes=data.get('processes'),
    )
    db.session.add(metric)
    db.session.commit()

    return jsonify({'status': 'ok'}), 200
