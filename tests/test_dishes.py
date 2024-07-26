import pytest
import sqlite3
from flask import Flask
from project_coffee.routes.dishes import DishesRoutes

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['DATABASE'] = 'test_database.db'
    app.config['UPLOAD_FOLDER'] = 'static'

    with app.app_context():
        DishesRoutes(app)
        yield app

    # Cleanup code
    if os.path.exists(app.config['DATABASE']):
        os.remove(app.config['DATABASE'])

@pytest.fixture
def client(app):
    return app.test_client()

def test_dishes_route(client):
    response = client.get('/dishes')
    assert response.status_code == 200
    assert b'Platillos' in response.data

def test_create_dish(client):
    dish_data = {
        'name': 'Test Dish',
        'price': 10.0,
        'preparation_time': 15,
        'image': (BytesIO(b'test image'), 'test.jpg')
    }
    response = client.post('/dishes', data=dish_data, content_type='multipart/form-data')
    assert response.status_code == 302  # Redirection after success
