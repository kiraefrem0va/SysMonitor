import pytest
from app import create_app, db
from app.models import Computer, Metric

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()

def test_api_metrics_requires_hostname(client, app):
    data = {
        'cpu': 10.0,
        'ram': 50.0,
        'disk': 70.0,
        'processes': 123
    }
    resp = client.post('/api/metrics', json=data)
    assert resp.status_code == 400
    assert b'hostname required' in resp.data

def test_api_metrics_creates_computer_and_metric(client, app):
    data = {
        'hostname': 'TEST-PC',
        'cpu': 20.5,
        'ram': 60.0,
        'disk': 80.0,
        'processes': 42
    }
    resp = client.post('/api/metrics', json=data)
    assert resp.status_code == 200

    with app.app_context():
        comp = Computer.query.filter_by(hostname='TEST-PC').first()
        assert comp is not None
        assert len(comp.metrics) == 1

        metric = comp.metrics[0]
        assert metric.cpu_percent == data['cpu']
        assert metric.memory_usage == data['ram']
        assert metric.disk_usage == data['disk']
        assert metric.processes == data['processes']