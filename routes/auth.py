from flask import Blueprint, render_template, request, redirect, url_for, session, g
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

class AuthRoutes:
    def __init__(self, app):
        """
        Inicializa el blueprint de autenticación y configura la base de datos.
        
        :param app: La instancia de la aplicación Flask.
        """
        self.blueprint = Blueprint('auth', __name__)
        self.app = app
        self.DATABASE = 'database.db'
        self.setup_routes()

    def setup_routes(self):
        """
        Configura las rutas para login, logout y registro de usuarios.
        """
        self.blueprint.route('/login', methods=['GET', 'POST'])(self.login)
        self.blueprint.route('/logout')(self.logout)
        self.blueprint.route('/register', methods=['GET', 'POST'])(self.register)

    def get_db(self):
        """
        Obtiene una conexión a la base de datos SQLite. Si no existe una conexión activa,
        se crea una nueva.
        
        :return: Conexión a la base de datos.
        """
        if not hasattr(g, '_database'):
            g._database = sqlite3.connect(self.DATABASE)
            g._database.row_factory = sqlite3.Row
        return g._database

    def login(self):
        """
        Maneja la lógica de inicio de sesión de usuarios.
        
        :return: Renderiza la plantilla de login o redirige al dashboard si las credenciales son válidas.
        """
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            db = self.get_db()
            cursor = db.execute('SELECT id, first_name, password FROM users WHERE email = ?', (email,))
            user = cursor.fetchone()
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['user_name'] = user['first_name']
                return redirect(url_for('dashboard'))
            return 'Invalid credentials', 401
        return render_template('login.html')

    def logout(self):
        """
        Maneja la lógica de cierre de sesión de usuarios.
        
        :return: Redirige a la página de login.
        """
        session.clear()
        return redirect(url_for('auth.login'))

    def register(self):
        """
        Maneja la lógica de registro de nuevos usuarios.
        
        :return: Renderiza la plantilla de registro o redirige a la página de login si el registro es exitoso.
        """
        if request.method == 'POST':
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            birthday = request.form['birthday']
            gender = request.form['gender']
            email = request.form['email']
            phone_number = request.form['phone_number']
            password = request.form['password']

            db = self.get_db()
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
