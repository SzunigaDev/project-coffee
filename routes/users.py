from flask import Blueprint, render_template, request, redirect, url_for, g
import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime
from .decorators import login_required

class UsersRoutes:
    def __init__(self, app):
        self.blueprint = Blueprint('users', __name__)
        self.app = app
        self.DATABASE = 'database.db'
        self.setup_routes()

    def setup_routes(self):
        self.blueprint.route('/users')(self.users)
        self.blueprint.route('/add_user', methods=['POST'])(self.add_user)

    def get_db(self):
        if not hasattr(g, '_database'):
            g._database = sqlite3.connect(self.DATABASE)
            g._database.row_factory = sqlite3.Row
        return g._database

    def format_date(self, date_str):
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%d/%b/%Y')

    def translate_gender(self, gender):
        translations = {
            'Male': 'Hombre',
            'Female': 'Mujer',
            'Other': 'Otro'
        }
        return translations.get(gender, gender)

    def format_phone(self, phone):
        if len(phone) == 10:
            return f"({phone[:3]}) {phone[3:6]}-{phone[6:]}"
        return phone

    @login_required
    def users(self):
        db = self.get_db()
        cursor = db.execute('SELECT id, first_name, last_name, birthday, gender, email, phone_number FROM users')
        users = cursor.fetchall()

        formatted_users = []
        for user in users:
            formatted_user = list(user)
            formatted_user[3] = self.format_date(user['birthday'])  # Formatear fecha
            formatted_user[4] = self.translate_gender(user['gender'])  # Traducir género
            formatted_user[6] = self.format_phone(user['phone_number'])  # Formatear teléfono
            formatted_users.append(formatted_user)

        return render_template('users.html', users=formatted_users)

    @login_required
    def add_user(self):
        db = self.get_db()
        hashed_password = generate_password_hash(request.form['password'])
        db.execute('''
            INSERT INTO users (first_name, last_name, birthday, gender, email, phone_number, password)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', [
            request.form['first_name'],
            request.form['last_name'],
            request.form['birthday'],
            request.form['gender'],
            request.form['email'],
            request.form['phone_number'],
            hashed_password
        ])
        db.commit()
        return redirect(url_for('users.users'))
