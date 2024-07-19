import pytest
from flask import session, url_for
from routes.decorators import login_required
from routes.auth import auth_bp
from tests.test_client import TestClient

app = TestClient.get_app()
app.config['SERVER_NAME'] = 'localhost'
app.register_blueprint(auth_bp, name='auth_decorator_test')

@app.route('/protected')
@login_required
def protected():
    return 'This is a protected route'

@pytest.fixture
def test_client():
    client = TestClient()
    client.init_db()
    yield client
    client.close()

def test_login_required_redirects_to_login(test_client):
    with app.app_context():
        response = test_client.client.get('/protected')
        assert response.status_code == 302
        assert url_for('auth_decorator_test.login', _external=False) in response.headers['Location']

def test_login_required_allows_access_when_logged_in(test_client):
    with test_client.client.session_transaction() as sess:
        sess['user_id'] = 1
    response = test_client.client.get('/protected')
    assert response.status_code == 200
    assert b'This is a protected route' in response.data
