import pytest
import sqlite3
from flask import Flask
from project_coffee.routes.orders import OrdersRoutes

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['DATABASE'] = 'test_database.db'

    with app.app_context():
        OrdersRoutes(app)
        yield app

    # Cleanup code
    if os.path.exists(app.config['DATABASE']):
        os.remove(app.config['DATABASE'])

@pytest.fixture
def client(app):
    return app.test_client()

def test_orders_route(client):
    response = client.get('/orders')
    assert response.status_code == 200
    assert b'Mesa' in response.data

def test_create_order(client):
    order_data = {
        'table_number': 1,
        'dishes': [{'id': 1, 'quantity': 2, 'price': 10.0}]
    }
    response = client.post('/orders/create', json=order_data)
    assert response.status_code == 200
    assert response.json['success'] == True

def test_complete_order(client):
    complete_data = {
        'order_id': 1,
        'payment_amount': 50.0
    }
    response = client.post('/orders/complete', json=complete_data)
    assert response.status_code == 200
    assert response.json['success'] == True
