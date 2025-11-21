import psutil
import requests
import time

class SystemMonitor:
    def collect_metrics(self):
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'processes': len(psutil.pids()),
            'timestamp': time.time()
            }
        
    def send_metrics(self, server_url, token):
        metrics = self.collect_metrics()
        try:
            response = requests.post(f'{server_url}/api/metrics', 
                                     json = metrics,
                                     headers = {'Authorization': f'Bearer {token}'}
                                     )
            return response.status_code == 200
        except:
            return False

if __name__ == '__main__':
    monitor = SystemMonitor()
    print('Собранные метрики:', monitor.collect_metrics())