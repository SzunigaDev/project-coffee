from flask import Blueprint, render_template, request, redirect, url_for, session, g
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        cursor = db.execute('SELECT id, first_name, password FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            return redirect(url_for('dashboard')) 
        return 'Invalid credentials', 401
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        birthday = request.form['birthday']
        gender = request.form['gender']
        email = request.form['email']
        phone_number = request.form['phone_number']
        password = request.form['password']

        db = get_db()
        cursor = db.execute('SELECT id FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        if user:
            return 'Email address already registered', 400

        hashed_password = generate_password_hash(password)
        db.execute('''
            INSERT INTO users (first_name, last_name, birthday, gender, email, phone_number, password)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (first_name, last_name, birthday, gender, email, phone_number, hashed_password))
        db.commit()
        return redirect(url_for('auth.login'))
    return render_template('register.html')
