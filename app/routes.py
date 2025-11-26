from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session
from functools import wraps
from .models import Computer, Metric
from . import db

main = Blueprint('main', __name__)

def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('main.login'))
        return view_func(*args, **kwargs)
    return wrapper

@main.route('/', methods=['GET', 'POST'])
@main.route('/login', methods=['GET', 'POST'])
def login():
    # если уже авторизованы — сразу на главную панель
    if session.get('logged_in'):
        return redirect(url_for('main.dashboard'))

    error = None

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # данные для админа
        if username == 'admin' and password == 'admin':
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('main.dashboard'))
        else:
            error = 'Неверный логин или пароль'

    return render_template('login.html', error=error)

@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))

@main.route('/dashboard')
@login_required
def dashboard():
    computers = Computer.query.all()
    total = len(computers)

    alerts = []
    cpu_values = []

    for comp in computers:
        last = comp.metrics[-1] if comp.metrics else None
        if not last:
            continue

        # для средней загрузки CPU
        cpu_values.append(last.cpu_percent or 0)

        problems_for_comp = []

        if last.disk_usage is not None and last.disk_usage >= 90:
            problems_for_comp.append(f"Диск: {int(last.disk_usage)}% заполнен")

        if last.memory_usage is not None and last.memory_usage >= 80:
            problems_for_comp.append(f"Высокая загрузка RAM: {int(last.memory_usage)}%")

        if last.cpu_percent is not None and last.cpu_percent >= 85:
            problems_for_comp.append(f"Высокая загрузка CPU: {int(last.cpu_percent)}%")

        if problems_for_comp:
            alerts.append({
                "computer": comp,
                "message": "; ".join(problems_for_comp),
                "timestamp": last.timestamp,
            })

    problems_count = len(alerts)
    avg_cpu = int(sum(cpu_values) / len(cpu_values)) if cpu_values else 0

    return render_template(
        'dashboard.html',
        total_computers=total,
        problems_count=problems_count,
        avg_cpu=avg_cpu,
        alerts=alerts,
    )

@main.route('/computers')
@login_required
def index():
    computers = Computer.query.all()
    return render_template('index.html', computers=computers)

@main.route('/api/metrics', methods=['POST'])
def receive_metrics():
    data = request.json
    if not data:
        return jsonify({'error': 'invalid json'}), 400

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
        cpu_percent=data.get('cpu'),
        memory_usage=data.get('ram'),
        disk_usage=data.get('disk'),
        processes=data.get('processes'),
    )

    db.session.add(metric)
    db.session.commit()

    return jsonify({'status': 'ok'}), 200

@main.route('/computer/<int:comp_id>')
@login_required
def computer_detail(comp_id):
    comp = Computer.query.get_or_404(comp_id)
    
    metrics = (
        Metric.query
        .filter_by(computer_id=comp.id)
        .order_by(Metric.id.desc())
        .limit(20)
        .all()
    )

    return render_template('detail.html', comp=comp, metrics=metrics)