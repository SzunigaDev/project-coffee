from flask import Blueprint, render_template, request, redirect, url_for, session, g, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from .decorators import login_required

class UsersRoutes:
    def __init__(self, app):
        """
        Inicializa el blueprint de usuarios y configura la base de datos.
        
        :param app: La instancia de la aplicación Flask.
        """
        self.blueprint = Blueprint('users', __name__)
        self.app = app
        self.DATABASE = 'database.db'
        self.UPLOAD_FOLDER = 'static/profile_pics'
        self.UPLOAD_FOLDER_NAME = 'profile_pics/'
        self.ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        self.setup_routes()
        if not os.path.exists(self.UPLOAD_FOLDER):
            os.makedirs(self.UPLOAD_FOLDER)

    def setup_routes(self):
        """
        Configura las rutas para la gestión de usuarios.
        """
        self.blueprint.route('/users')(self.users)
        self.blueprint.route('/user/<int:user_id>', methods=['GET'])(self.get_user)
        self.blueprint.route('/add_user', methods=['POST'])(self.add_user)
        self.blueprint.route('/update_user/<int:user_id>', methods=['POST'])(self.update_user)
        self.blueprint.route('/profile')(self.profile)
        self.blueprint.route('/edit_profile', methods=['GET', 'POST'])(self.edit_profile)

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

    def allowed_file(self, filename):
        """
        Verifica si un archivo tiene una extensión permitida.
        
        :param filename: El nombre del archivo.
        :return: True si la extensión del archivo está permitida, False en caso contrario.
        """
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

    @login_required
    def users(self):
        """
        Maneja la lógica para la página de gestión de usuarios, recuperando todos los usuarios
        y formateando sus datos.
        
        :return: Renderiza la plantilla 'users.html' con los datos de los usuarios.
        """
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
    def profile(self):
        """
        Maneja la lógica para mostrar el perfil del usuario actual.
        
        :return: Renderiza la plantilla 'profile.html' con los datos del usuario.
        """
        db = self.get_db()
        user_id = session.get('user_id')
        user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        return render_template('profile.html', user=user)

    @login_required
    def edit_profile(self):
        """
        Maneja la lógica para editar el perfil del usuario actual.
        
        :return: Renderiza la plantilla 'edit_profile.html' con los datos del usuario o redirige después de actualizar.
        """
        db = self.get_db()
        user_id = session.get('user_id')
        user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        
        if request.method == 'POST':
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            birthday = request.form['birthday']
            gender = request.form['gender']
            email = request.form['email']
            phone_number = request.form['phone_number']
            bio = request.form['bio']
            address = request.form['address']

            if 'profile_picture' in request.files:
                file = request.files['profile_picture']
                if file and self.allowed_file(file.filename):
                    filepath = os.path.join(self.UPLOAD_FOLDER, str(session.get('user_id')))
                    file.save(filepath)
                    filepath_name = self.UPLOAD_FOLDER_NAME+str(session.get('user_id'))
                    db.execute('UPDATE users SET profile_picture = ? WHERE id = ?', (filepath_name, user_id))

            db.execute('''
                UPDATE users 
                SET first_name = ?, last_name = ?, birthday = ?, gender = ?, email = ?, phone_number = ?, bio = ?, address = ?
                WHERE id = ?
            ''', (first_name, last_name, birthday, gender, email, phone_number, bio, address, user_id))
            db.commit()
            return redirect(url_for('users.profile'))

        return render_template('edit_profile.html', user=user)

    def format_date(self, date_str):
        """
        Formatea una fecha en formato 'YYYY-MM-DD' a 'DD/MMM/YYYY'.
        
        :param date_str: La fecha en formato 'YYYY-MM-DD'.
        :return: La fecha formateada en 'DD/MMM/YYYY'.
        """
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%d/%b/%Y')

    def translate_gender(self, gender):
        """
        Traduce el género de inglés a español.
        
        :param gender: El género en inglés.
        :return: El género traducido al español.
        """
        translations = {
            'Male': 'Hombre',
            'Female': 'Mujer',
            'Other': 'Otro'
        }
        return translations.get(gender, gender)

    def format_phone(self, phone):
        """
        Formatea un número de teléfono a un formato más legible.
        
        :param phone: El número de teléfono.
        :return: El número de teléfono formateado.
        """
        if len(phone) == 10:
            return f"({phone[:3]}) {phone[3:6]}-{phone[6:]}"
        return phone

    @login_required
    def get_user(self, user_id):
        db = self.get_db()
        user = db.execute('SELECT id, first_name, last_name, birthday, gender, email, phone_number FROM users WHERE id = ?', (user_id,)).fetchone()
        if user:
            user = dict(user)
            user['birthday'] = datetime.strptime(user['birthday'], '%Y-%m-%d').strftime('%Y-%m-%d')
        return jsonify(user)
    
    @login_required
    def add_user(self):
        """
        Maneja la lógica para agregar un nuevo usuario.
        
        :return: Redirige a la página de gestión de usuarios después de agregar el usuario.
        """
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

    @login_required
    def update_user(self, user_id):
        db = self.get_db()
        db.execute('''
            UPDATE users SET first_name = ?, last_name = ?, birthday = ?, gender = ?, email = ?, phone_number = ?
            WHERE id = ?
        ''', [
            request.form['first_name'],
            request.form['last_name'],
            request.form['birthday'],
            request.form['gender'],
            request.form['email'],
            request.form['phone_number'],
            user_id
        ])
        db.commit()
        return redirect(url_for('users.users'))