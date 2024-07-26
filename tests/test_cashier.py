import pytest
import sqlite3
from flask import Flask
from project_coffee.routes.cashier import CashierRoutes

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['DATABASE'] = 'test_database.db'

    with app.app_context():
        CashierRoutes(app)
        yield app

    # Cleanup code
    if os.path.exists(app.config['DATABASE']):
        os.remove(app.config['DATABASE'])

@pytest.fixture
def client(app):
    return app.test_client()

def test_cashier_route(client):
    response = client.get('/cashier')
    assert response.status_code == 200
    assert b'Caja Registradora' in response.data

def test_group_orders(client):
    group_data = {
        'table_number': 1
    }
    response = client.post('/cashier/group_orders', json=group_data)
    assert response.status_code == 200
    assert 'grouped_orders' in response.json
    assert 'total_amount' in response.json
