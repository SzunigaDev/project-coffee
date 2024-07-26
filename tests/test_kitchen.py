import pytest
import sqlite3
from flask import Flask
from project_coffee.routes.kitchen import KitchenRoutes

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['DATABASE'] = 'test_database.db'

    with app.app_context():
        KitchenRoutes(app)
        yield app

    # Cleanup code
    if os.path.exists(app.config['DATABASE']):
        os.remove(app.config['DATABASE'])

@pytest.fixture
def client(app):
    return app.test_client()

def test_kitchen_route(client):
    response = client.get('/kitchen')
    assert response.status_code == 200
    assert b'Mesa' in response.data
