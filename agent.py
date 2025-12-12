"""
Модуль агента SysMonitor.

Отвечает за сбор основных системных метрик (CPU, RAM, диск, количество процессов)
и периодическую отправку этих данных на сервер SysMonitor по HTTP.
"""

import psutil
import shutil
import requests
import time
import socket
import platform

class SystemMonitor:
    """
    Класс для сбора и отправки системных метрик с рабочей станции.

    Использует библиотеки psutil и shutil для доступа к информации о загрузке CPU,
    использованной оперативной памяти, дисковом пространстве и количестве процессов.
    """
    def collect_metrics(self):
        """
        Собрать текущие метрики системы.

        Определяет корректный путь к системному диску в зависимости от операционной
        системы, вычисляет процент его заполнения и возвращает словарь с основными
        показателями.

        :return: словарь с ключами:
                 - hostname: имя компьютера;
                 - cpu: текущая загрузка CPU в процентах;
                 - ram: использование оперативной памяти в процентах;
                 - disk: заполненность системного диска в процентах;
                 - processes: количество запущенных процессов.
        :rtype: dict
        """
        system = platform.system()
        if system == 'Windows':
            disk_path = 'C:\\'
        else:
            disk_path = '/'

        disk_info = shutil.disk_usage(disk_path)
        total_disk = disk_info.total
        used_disk = disk_info.used
        disk_percent = (used_disk / total_disk) * 100 if total_disk > 0 else 0

        return {
            'hostname': socket.gethostname(),
            'cpu': psutil.cpu_percent(interval=1),
            'ram': psutil.virtual_memory().percent,
            'disk': round(disk_percent, 1),
            'processes': len(psutil.pids()),
        }

    def send_metrics(self, server_url):
        """
        Отправить собранные метрики на сервер SysMonitor.

        Формирует HTTP POST-запрос к эндпоинту /api/metrics, передавая метрики
        в формате JSON. В случае успешного ответа сервера (код 200) возвращает True.

        :param server_url: базовый URL сервера SysMonitor
                           (например, "http://192.168.1.176:5000").
        :type server_url: str
        :return: True, если отправка прошла успешно, иначе False.
        :rtype: bool
        """
        metrics = self.collect_metrics()
        try:
            response = requests.post(
                f'{server_url}/api/metrics',
                json=metrics,
            )
            print("Ответ сервера:", response.status_code, response.text)
            return response.status_code == 200
        except Exception as e:
            print("Ошибка отправки:", e)
            return False


if __name__ == '__main__':
    """
    Точка входа при запуске агента как самостоятельного скрипта.

    Инициализирует объект SystemMonitor и в бесконечном цикле
    собирает и отправляет метрики на указанный сервер SysMonitor.
    """
    # базовый адрес сервера SysMonitor (может быть заменён на внешний IP)
    server = 'http://127.0.0.1:5000'

    # объект, отвечающий за сбор и отправку системных метрик
    monitor = SystemMonitor()
    print('Собранные метрики:', monitor.collect_metrics())
    
    while True:
        print('Отправка:', monitor.send_metrics(server))
        time.sleep(5)