import sqlite3
from werkzeug.security import generate_password_hash
import os

DATABASE = 'database.db'
# Eliminar la base de datos existente
if os.path.exists(DATABASE):
    os.remove(DATABASE)

# Crear la conexión a la base de datos
conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

# Crear tabla de usuarios
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    birthday TEXT,
    gender TEXT,
    email TEXT NOT NULL UNIQUE,
    phone_number TEXT,
    profile_picture TEXT,
    bio TEXT,
    address TEXT,
    password TEXT NOT NULL
)
''')

# Crear tabla de platillos
cursor.execute('''
CREATE TABLE IF NOT EXISTS dishes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    preparation_time INTEGER NOT NULL,
    img_url TEXT
)
''')

# Crear tabla de pedidos
cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_number INTEGER NOT NULL,
    order_number INTEGER NOT NULL,
    order_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL,
    total_amount REAL,
    payment_amount REAL,
    change_amount REAL,
    cashier_id INTEGER,
    FOREIGN KEY (cashier_id) REFERENCES users(id)
)
''')

# Crear tabla de items de pedido
cursor.execute('''
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    dish_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    price REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (dish_id) REFERENCES dishes(id)
)
''')

# Insertar usuarios por defecto
users = [
    ('Admin', 'Admin', '2000-01-01', 'Hombre', 'admin@mail.com', '6564567890', generate_password_hash('1234')),
    ('Sergio', 'Zuniga', '1990-12-01', 'Hombre', 'szuniga@mail.com', '6567654321', generate_password_hash('123456789'))
]
cursor.executemany('''
    INSERT INTO users (first_name, last_name, birthday, gender, email, phone_number, password)
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', users)

# Insertar platillos por defecto
dishes = [
    ('Chiles en Nogada', 120.00, 30, '/static/chiles-en-nogada.webp'),
    ('Menudo', 80.00, 45, '/static/menudo.webp'),
    ('Mole', 100.00, 40, '/static/mole.webp'),
    ('Pozole', 90.00, 35, '/static/pozole.webp'),
    ('Tamales', 50.00, 20, '/static/tamales.webp')
]
cursor.executemany('''
    INSERT INTO dishes (name, price, preparation_time, img_url)
    VALUES (?, ?, ?, ?)
''', dishes)

# Confirmar los cambios y cerrar la conexión
conn.commit()
conn.close()

print("Base de datos inicializada con datos por defecto.")
