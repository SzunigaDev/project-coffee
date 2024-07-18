from flask import Blueprint, render_template, request, redirect, url_for, g
import sqlite3
from werkzeug.security import generate_password_hash
from .decorators import login_required
from datetime import datetime


users_bp = Blueprint('users', __name__)

DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def format_date(date_str):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    return date_obj.strftime('%d/%b/%Y')

def translate_gender(gender):
    translations = {
        'Male': 'Hombre',
        'Female': 'Mujer',
        'Other': 'Otro'
    }
    return translations.get(gender, gender)

def format_phone(phone):
    if len(phone) == 10:
        return f"({phone[:3]}) {phone[3:6]}-{phone[6:]}"
    return phone

@users_bp.route('/users')
@login_required
def users():
    db = get_db()
    cursor = db.execute('SELECT id, first_name, last_name, birthday, gender, email, phone_number FROM users')
    users = cursor.fetchall()

    formatted_users = []
    for user in users:
        formatted_user = list(user)
        formatted_user[3] = format_date(user[3])  # Formatear fecha
        formatted_user[4] = translate_gender(user[4])  # Traducir género
        formatted_user[6] = format_phone(user[6])  # Formatear teléfono
        formatted_users.append(formatted_user)

    return render_template('users.html', users=formatted_users)

@users_bp.route('/add_user', methods=['POST'])
@login_required
def add_user():
    db = get_db()
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
