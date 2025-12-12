"""
Точка входа для запуска серверной части SysMonitor.

Создаёт экземпляр Flask-приложения через фабрику create_app()
и запускает встроенный веб-сервер на всех интерфейсах хоста.
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    print('Запуск SysMonitor сервера...')
    app.run(debug=True, host='0.0.0.0', port=5000)

