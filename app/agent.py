import psutil
import shutil
import requests
import time
import socket
import platform

class SystemMonitor:
    def collect_metrics(self):
        # определяем правильный путь для диска
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
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': round(disk_percent, 1),
            'processes': len(psutil.pids()),
            'timestamp': time.time()
        }

    def send_metrics(self, server_url, token):
        metrics = self.collect_metrics()
        try:
            response = requests.post(
                f'{server_url}/api/metrics',
                json=metrics,
                headers={'Authorization': f'Bearer {token}'}
            )
            print("Ответ сервера:", response.status_code, response.text)
            return response.status_code == 200
        except Exception as e:
            print("Ошибка отправки:", e)
            return False


if __name__ == '__main__':
    server = 'http://127.0.0.1:5000'
    token = 'kira-token'

    monitor = SystemMonitor()
    print('Собранные метрики:', monitor.collect_metrics())
    print('Отправка:', monitor.send_metrics(server, token))