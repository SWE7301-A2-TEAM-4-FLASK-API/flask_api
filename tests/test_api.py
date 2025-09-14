import pytest
from api.main import app, db
from api.models import User

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def test_register_and_login(client):
    # Register
    response = client.post('/register', json={
        'username': 'testuser',
        'password': 'Testpass123!',
        'email': 'test@example.com',
        'role': 'user'
    })
    assert response.status_code == 201

    # Login
    response = client.post('/login', json={
        'username': 'testuser',
        'password': 'Testpass123!'
    })
    assert response.status_code == 201
    token = response.get_json()['access_token']
    assert token

def test_telemetry_create(client):
    # Register and login to get token
    client.post('/register', json={
        'username': 'teleuser',
        'password': 'Telepass123!',
        'email': 'tele@example.com',
        'role': 'user'
    })
    login_resp = client.post('/login', json={
        'username': 'teleuser',
        'password': 'Telepass123!'
    })
    token = login_resp.get_json()['access_token']

    # Create telemetry
    response = client.post('/telemetry', json={
        'buoy_id': 1,
        'salinity': 35.2,
        'pH': 8.1,
        'temperature': 23.3,
        'pollutants': 'none',
        'location': 'Gulf of Guinea'
    }, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 201
    data = response.get_json()
    assert 'id' in data or 'data' in data