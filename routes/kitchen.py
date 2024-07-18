from flask import Blueprint, render_template, g
import sqlite3
from .decorators import login_required

kitchen_bp = Blueprint('kitchen', __name__)

DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@kitchen_bp.route('/kitchen')
@login_required
def kitchen():
    db = get_db()
    orders = db.execute('SELECT * FROM orders WHERE status = ? ORDER BY order_time', ('Pendiente',)).fetchall()
    orders_with_items = []
    priority = 1
    for order in orders:
        items = db.execute('SELECT dish_id, quantity, price FROM order_items WHERE order_id = ?', (order[0],)).fetchall()
        order_items = []
        for item in items:
            dish = db.execute('SELECT name FROM dishes WHERE id = ?', (item[0],)).fetchone()
            order_items.append({
                'name': dish[0],
                'quantity': item[1],
                'price': item[2]
            })
        orders_with_items.append({
            'id': order[0],
            'table_number': order[1],
            'order_time': order[2],
            'status': order[3],
            'total_amount': order[4],
            'items': order_items,
            'priority': priority  # Agregar prioridad
        })
        priority += 1
    return render_template('kitchen.html', orders=orders_with_items)
