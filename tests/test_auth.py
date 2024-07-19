import pytest
from werkzeug.security import generate_password_hash
from tests.test_client import TestClient
from application import get_db, app

@pytest.fixture
def test_client():
    client = TestClient()
    client.init_db()
    yield client
    client.close()

def test_register(test_client):
    test_client.clear_db()
    response = test_client.client.post('/register', data={
        'first_name': 'Test',
        'last_name': 'User',
        'birthday': '1990-01-01',
        'gender': 'Other',
        'email': 'testuser@example.com',
        'phone_number': '1234567890',
        'password': 'password'
    })
    assert response.status_code == 302
    assert '/login' in response.headers['Location']

def test_register_existing_email(test_client):
    test_client.clear_db()
    with app.app_context():
        db = get_db()
        db.execute('INSERT INTO users (first_name, last_name, birthday, gender, email, phone_number, password) VALUES (?, ?, ?, ?, ?, ?, ?)', (
            'Existing', 'User', '1990-01-01', 'Other', 'existinguser@example.com', '1234567890', generate_password_hash('password')
        ))
        db.commit()

    response = test_client.client.post('/register', data={
        'first_name': 'Test',
        'last_name': 'User',
        'birthday': '1990-01-01',
        'gender': 'Other',
        'email': 'existinguser@example.com',
        'phone_number': '1234567890',
        'password': 'password'
    })
    assert response.status_code == 400
    assert b'Email address already registered' in response.data

def test_login(test_client):
    test_client.clear_db()
    with app.app_context():
        db = get_db()
        db.execute('INSERT INTO users (first_name, last_name, birthday, gender, email, phone_number, password) VALUES (?, ?, ?, ?, ?, ?, ?)', (
            'Test', 'User', '1990-01-01', 'Other', 'testuser@example.com', '1234567890', generate_password_hash('password')
        ))
        db.commit()

    response = test_client.client.post('/login', data={
        'email': 'testuser@example.com',
        'password': 'password'
    })
    assert response.status_code == 302
    assert '/' in response.headers['Location']
    with test_client.client.session_transaction() as sess:
        assert sess['user_id'] is not None
        assert sess['user_name'] == 'Test'

def test_login_invalid_credentials(test_client):
    test_client.clear_db()
    response = test_client.client.post('/login', data={
        'email': 'nonexistent@example.com',
        'password': 'password'
    })
    assert response.status_code == 401
    assert b'Invalid credentials' in response.data

def test_logout(test_client):
    with test_client.client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['user_name'] = 'Test'

    response = test_client.client.get('/logout')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']
    with test_client.client.session_transaction() as sess:
        assert 'user_id' not in sess
        assert 'user_name' not in sess
