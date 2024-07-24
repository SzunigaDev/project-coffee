from flask import Blueprint, render_template, request, redirect, url_for, g
import sqlite3
import os
from werkzeug.utils import secure_filename
from .decorators import login_required

class DishesRoutes:
    def __init__(self, app):
        """
        Inicializa el blueprint de platos y configura la base de datos, 
        la carpeta de subida y las extensiones permitidas.
        
        :param app: La instancia de la aplicación Flask.
        """
        self.blueprint = Blueprint('dishes', __name__)
        self.app = app
        self.DATABASE = 'database.db'
        self.UPLOAD_FOLDER = 'static'
        self.ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        self.setup_routes()

    def setup_routes(self):
        """
        Configura las rutas para la gestión de platos.
        """
        self.blueprint.route('/dishes', methods=['GET', 'POST'])(self.dishes)
        self.blueprint.route('/dishes/edit/<int:id>', methods=['GET', 'POST'])(self.edit_dish)
        self.blueprint.route('/dishes/delete/<int:id>', methods=['POST'])(self.delete_dish)

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
        Verifica si el archivo tiene una extensión permitida.
        
        :param filename: Nombre del archivo a verificar.
        :return: True si la extensión del archivo es permitida, False de lo contrario.
        """
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

    @login_required
    def dishes(self):
        """
        Maneja la lógica para la página de gestión de platos, permitiendo crear
        y listar platos.
        
        :return: Renderiza la plantilla 'dishes.html' con los datos de los platos.
        """
        db = self.get_db()
        if request.method == 'POST':
            name = request.form['name']
            price = request.form['price']
            preparation_time = request.form['preparation_time']
            
            if 'image' not in request.files:
                return 'No file part'
            file = request.files['image']
            if file.filename == '':
                return 'No selected file'
            if file and self.allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(self.UPLOAD_FOLDER, filename))
                img_url = f'/static/{filename}'
                db.execute('INSERT INTO dishes (name, price, preparation_time, img_url) VALUES (?, ?, ?, ?)', 
                           (name, price, preparation_time, img_url))
                db.commit()
                return redirect(url_for('dishes.dishes'))
        
        dishes = db.execute('SELECT * FROM dishes').fetchall()
        return render_template('dishes.html', dishes=dishes)

    @login_required
    def edit_dish(self, id):
        """
        Maneja la lógica para la edición de un plato existente.
        
        :param id: ID del plato a editar.
        :return: Renderiza la plantilla 'edit_dish.html' con los datos del plato a editar.
        """
        db = self.get_db()
        if request.method == 'POST':
            name = request.form['name']
            price = request.form['price']
            preparation_time = request.form['preparation_time']
            
            if 'image' in request.files and request.files['image'].filename != '':
                file = request.files['image']
                if file and self.allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(self.UPLOAD_FOLDER, filename))
                    img_url = f'/static/{filename}'
                    db.execute('UPDATE dishes SET name = ?, price = ?, preparation_time = ?, img_url = ? WHERE id = ?', 
                               (name, price, preparation_time, img_url, id))
            else:
                db.execute('UPDATE dishes SET name = ?, price = ?, preparation_time = ? WHERE id = ?', 
                           (name, price, preparation_time, id))
            
            db.commit()
            return redirect(url_for('dishes.dishes'))
        
        dish = db.execute('SELECT * FROM dishes WHERE id = ?', (id,)).fetchone()
        return render_template('edit_dish.html', dish=dish)

    @login_required
    def delete_dish(self, id):
        """
        Maneja la lógica para eliminar un plato existente.
        
        :param id: ID del plato a eliminar.
        :return: Redirige a la página de gestión de platos después de eliminar el plato.
        """
        db = self.get_db()
        db.execute('DELETE FROM dishes WHERE id = ?', (id,))
        db.commit()
        return redirect(url_for('dishes.dishes'))
