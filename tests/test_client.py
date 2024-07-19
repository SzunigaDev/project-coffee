import os
import tempfile
import sqlite3
from flask import g
from application import app, get_db

class TestClient:
    def __init__(self):
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.client = app.test_client()

    def init_db(self):
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                birthday TEXT,
                gender TEXT,
                email TEXT NOT NULL UNIQUE,
                phone_number TEXT,
                password TEXT NOT NULL
            )
            ''')
            db.commit()

    def clear_db(self):
        with app.app_context():
            db = get_db()
            db.execute('DELETE FROM users')
            db.commit()

    def close(self):
        with app.app_context():
            get_db().close()
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

    @staticmethod
    def get_app():
        return app
