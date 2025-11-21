from flask import Blueprint, render_template, jsonify

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return 'SysMonitor - Главная страница (будет реализован интерфейс)'

@main.route('/api/computers')
def get_computers():
    computers = [
        {
            'name': 'Web-Server-01',
            'status': 'online',
            'cpu': 25,
            'ram': 40,
            'disk': 95
            },
        {
            'name': 'DB-Server-02',
            'status': 'online',
            'cpu': 65,
            'ram': 89,
            'disk': 45
            }
        ]
    return jsonify(computers)