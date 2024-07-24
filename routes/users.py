from flask import Blueprint, render_template, request, redirect, url_for, g, session
import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime
from .decorators import login_required
from werkzeug.utils import secure_filename
import os


class UsersRoutes:
    def __init__(self, app):
        """
        Inicializa el blueprint de usuarios y configura la base de datos.
        
        :param app: La instancia de la aplicación Flask.
        """
        self.blueprint = Blueprint('users', __name__)
        self.app = app
        self.DATABASE = 'database.db'
        self.setup_routes()

    def setup_routes(self):
        """
        Configura las rutas para la gestión de usuarios.
        """
        self.blueprint.route('/users')(self.users)
        self.blueprint.route('/add_user', methods=['POST'])(self.add_user)
        self.blueprint.route('/profile', methods=['GET', 'POST'])(self.profile)
        self.blueprint.route('/edit_profile', methods=['GET', 'POST'])(self.edit_profile)

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
    def profile(self):
        """
        Maneja la lógica para ver el perfil de un usuario.
        
        :return: Renderiza la plantilla 'profile.html' con los datos del usuario.
        """
        db = self.get_db()
        user_id = session['user_id']
        user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

        return render_template('profile.html', user=user)

    @login_required
    def edit_profile(self):
        """
        Maneja la lógica para editar el perfil de un usuario.
        
        :return: Renderiza la plantilla 'edit_profile.html' o redirige al perfil después de actualizar.
        """
        db = self.get_db()
        user_id = session['user_id']

        if request.method == 'POST':
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            birthday = request.form['birthday']
            gender = request.form['gender']
            email = request.form['email']
            phone_number = request.form['phone_number']
            bio = request.form['bio']
            address = request.form['address']

            # Manejar la carga de la imagen del perfil
            profile_picture = None
            if 'profile_picture' in request.files:
                file = request.files['profile_picture']
                if file.filename != '':
                    filename = secure_filename(file.filename)
                    file.save(os.path.join('static/profile_pics', filename))
                    profile_picture = f'profile_pics/{filename}'

            if profile_picture:
                db.execute('''
                    UPDATE users SET first_name = ?, last_name = ?, birthday = ?, gender = ?, email = ?, phone_number = ?, bio = ?, address = ?, profile_picture = ?
                    WHERE id = ?
                ''', (first_name, last_name, birthday, gender, email, phone_number, bio, address, profile_picture, user_id))
            else:
                db.execute('''
                    UPDATE users SET first_name = ?, last_name = ?, birthday = ?, gender = ?, email = ?, phone_number = ?, bio = ?, address = ?
                    WHERE id = ?
                ''', (first_name, last_name, birthday, gender, email, phone_number, bio, address, user_id))

            db.commit()
            return redirect(url_for('users.profile'))

        user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        return render_template('edit_profile.html', user=user)
