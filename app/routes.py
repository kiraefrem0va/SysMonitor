from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session
from functools import wraps
from .models import Computer, Metric
from . import db

main = Blueprint('main', __name__)

# значения по умолчанию
DEFAULT_CPU_THRESHOLD = 85
DEFAULT_RAM_THRESHOLD = 80
DEFAULT_DISK_THRESHOLD = 90

def get_thresholds():
    """
    Получить актуальные пороговые значения оповещений.

    Считывает значения порогов для CPU, RAM и диска из серверной сессии
    пользователя. Если пользователь ещё не настраивал пороги, возвращаются
    значения по умолчанию.

    :return: словарь с ключами "cpu", "ram", "disk" и значениями в процентах.
    :rtype: dict
    """
    return {
        'cpu': session.get('cpu_threshold', DEFAULT_CPU_THRESHOLD),
        'ram': session.get('ram_threshold', DEFAULT_RAM_THRESHOLD),
        'disk': session.get('disk_threshold', DEFAULT_DISK_THRESHOLD),
    }

main = Blueprint('main', __name__)

def login_required(view_func):
    """
    Декоратор для защиты маршрутов, требующих авторизации пользователя.

    Проверяет, авторизован ли пользователь в текущей сессии.
    Если пользователь не вошёл в систему, происходит перенаправление
    на страницу входа. В противном случае вызывается исходная функция
    обработчика маршрута.

    Используется для ограничения доступа к страницам.

    :param view_func: функция-обработчик маршрута Flask
    :type view_func: callable
    :return: обёрнутая функция с проверкой авторизации
    :rtype: callable
    """
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        """
        Внутренняя функция-обёртка.

        Проверяет наличие флага 'logged_in' в сессии пользователя.
        При отсутствии флага выполняется перенаправление на страницу логина.
        """
        if not session.get('logged_in'):
            return redirect(url_for('main.login'))
        return view_func(*args, **kwargs)
    return wrapper

@main.route('/', methods=['GET', 'POST'])
@main.route('/login', methods=['GET', 'POST'])
def login():
    """
    Страница входа в систему SysMonitor.

    Обрабатывает ввод логина и пароля, устанавливает признак авторизации в сессии.
    В учебных целях используется упрощённая проверка учётных данных (admin/admin).
    """
    if session.get('logged_in'):
        return redirect(url_for('main.dashboard'))

    error = None

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if username == 'admin' and password == 'admin':
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('main.dashboard'))
        else:
            error = 'Неверный логин или пароль'

    return render_template('login.html', error=error)

@main.route('/logout')
def logout():
    """
    Выход пользователя из системы.

    Очищает серверную сессию пользователя, удаляя признаки авторизации,
    после чего перенаправляет на страницу входа.
    
    :return: перенаправление на маршрут входа (login).
    """
    session.clear()
    return redirect(url_for('main.login'))

@main.route('/dashboard')
@login_required
def dashboard():
    """
    Главная панель администратора.

    Отображает общее количество компьютеров, число проблемных машин,
    среднюю загрузку CPU и список активных предупреждений.
    """
    computers = Computer.query.all()
    total = len(computers)

    alerts = []
    cpu_values = []

    thresholds = get_thresholds()

    for comp in computers:
        last = comp.metrics[-1] if comp.metrics else None
        if not last:
            continue

        # для средней загрузки CPU
        cpu_values.append(last.cpu_percent or 0)

        problems_for_comp = []

        if last.disk_usage is not None and last.disk_usage >= thresholds['disk']:
            problems_for_comp.append(f"Диск: {int(last.disk_usage)}% заполнен")

        if last.memory_usage is not None and last.memory_usage >= thresholds['ram']:
            problems_for_comp.append(f"Высокая загрузка RAM: {int(last.memory_usage)}%")

        if last.cpu_percent is not None and last.cpu_percent >= thresholds['cpu']:
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
        thresholds=thresholds
    )

@main.route('/alerts-settings', methods=['GET', 'POST'])
@login_required
def alerts_settings():
    """
    Страница настройки пороговых значений оповещений.

    Позволяет задать пороги для CPU, RAM и диска. Значения сохраняются в сессии
    и используются при формировании списка предупреждений на главной панели.
    """
    thresholds = get_thresholds()
    message = None
    error = None

    if request.method == 'POST':
        try:
            cpu = int(request.form.get('cpu_threshold', thresholds['cpu']))
            ram = int(request.form.get('ram_threshold', thresholds['ram']))
            disk = int(request.form.get('disk_threshold', thresholds['disk']))

            # ограничение
            cpu = max(0, min(cpu, 100))
            ram = max(0, min(ram, 100))
            disk = max(0, min(disk, 100))

            session['cpu_threshold'] = cpu
            session['ram_threshold'] = ram
            session['disk_threshold'] = disk

            thresholds = {'cpu': cpu, 'ram': ram, 'disk': disk}
            message = "Настройки сохранены"

            return redirect(url_for('main.alerts_settings'))
        except ValueError:
            error = "Введите целые числа от 0 до 100"

    return render_template(
        'alerts_settings.html',
        thresholds=thresholds,
        message=message,
        error=error,
    )

@main.route('/computers')
@login_required
def index():
    """
    Страница списка компьютеров.

    Показывает все зарегистрированные рабочие станции с последними метриками,
    позволяет перейти к детальному просмотру выбранного компьютера.
    """
    computers = Computer.query.all()
    return render_template('index.html', computers=computers)

@main.route('/api/metrics', methods=['POST'])
def receive_metrics():
    """
    Приём системных метрик от удалённого агента SysMonitor.

    Ожидает POST-запрос с JSON-объектом, содержащим основные параметры
    рабочей станции: загрузку CPU, использование RAM, заполненность диска,
    количество процессов и имя компьютера (hostname). Если компьютер ранее
    не был зарегистрирован в системе, создаётся новая запись в базе данных.

    После успешного приёма создаётся объект Metric, связанный с соответствующим
    компьютером, и сохраняется в базе данных.

    Формат входящего JSON:
        {
            "hostname": "DESKTOP-01",
            "cpu": 23.5,
            "ram": 58.0,
            "disk": 72.1,
            "processes": 142
        }

    Ошибки:
        - 400: если JSON отсутствует или отсутствует обязательное поле hostname.

    :return: JSON-ответ {"status": "ok"} при успешном сохранении метрик.
    :rtype: flask.Response
    """
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
    """
    Детальная страница компьютера.

    :param comp_id: идентификатор компьютера в базе данных.
    :type comp_id: int
    """
    comp = Computer.query.get_or_404(comp_id)
    
    metrics = (
        Metric.query
        .filter_by(computer_id=comp.id)
        .order_by(Metric.id.desc())
        .limit(20)
        .all()
    )

    return render_template('detail.html', comp=comp, metrics=metrics)