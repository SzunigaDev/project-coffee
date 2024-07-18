from flask import Blueprint, render_template, request, redirect, url_for, g
import sqlite3
import os
from werkzeug.utils import secure_filename
from .decorators import login_required

dishes_bp = Blueprint('dishes', __name__)

DATABASE = 'database.db'
UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@dishes_bp.route('/dishes', methods=['GET', 'POST'])
@login_required
def dishes():
    db = get_db()
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        preparation_time = request.form['preparation_time']
        
        # Manejar la carga de archivos
        if 'image' not in request.files:
            return 'No file part'
        file = request.files['image']
        if file.filename == '':
            return 'No selected file'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            img_url = f'/static/{filename}'
            db.execute('INSERT INTO dishes (name, price, preparation_time, img_url) VALUES (?, ?, ?, ?)', 
                       (name, price, preparation_time, img_url))
            db.commit()
            return redirect(url_for('dishes.dishes'))
    
    dishes = db.execute('SELECT * FROM dishes').fetchall()
    return render_template('dishes.html', dishes=dishes)

@dishes_bp.route('/dishes/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_dish(id):
    db = get_db()
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        preparation_time = request.form['preparation_time']
        
        # Manejar la carga de archivos
        if 'image' in request.files and request.files['image'].filename != '':
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
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

@dishes_bp.route('/dishes/delete/<int:id>', methods=['POST'])
@login_required
def delete_dish(id):
    db = get_db()
    db.execute('DELETE FROM dishes WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('dishes.dishes'))
