import agent
from agent import SystemMonitor

def test_collect_metrics_basic():
    monitor = SystemMonitor()
    data = monitor.collect_metrics()

    assert isinstance(data, dict)
    for key in ['hostname', 'cpu', 'ram', 'disk', 'processes']:
        assert key in data

    assert isinstance(data['cpu'], (int, float))
    assert isinstance(data['ram'], (int, float))
    assert isinstance(data['disk'], (int, float))
    assert isinstance(data['processes'], int)


def test_send_metrics_success(monkeypatch):
    monitor = agent.SystemMonitor()

    def fake_post(url, json):
        class FakeResponse:
            def __init__(self):
                self.status_code = 200
                self.text = 'OK'
        return FakeResponse()

    monkeypatch.setattr(agent.requests, 'post', fake_post)

    ok = monitor.send_metrics('http://blablafake:5000')
    assert ok is True