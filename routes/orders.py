from flask import Blueprint, render_template, request, redirect, url_for, g, jsonify, session
import sqlite3
from datetime import datetime
from .decorators import login_required

orders_bp = Blueprint('orders', __name__)

DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@orders_bp.route('/orders', methods=['GET', 'POST'])
@login_required
def orders():
    db = get_db()
    orders = db.execute('SELECT * FROM orders').fetchall()
    dishes = db.execute('SELECT * FROM dishes').fetchall()
    return render_template('orders.html', orders=orders, dishes=dishes)


@orders_bp.route('/orders/create', methods=['POST'])
@login_required
def create_order():
    db = get_db()
    data = request.get_json()
    table_number = data['table_number']
    dishes = data['dishes']
    order_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Obtener la hora actual

    db.execute('INSERT INTO orders (table_number, order_time, status) VALUES (?, ?, ?)', (table_number, order_time, 'Pendiente'))
    order_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]

    total_amount = 0
    for dish in dishes:
        db.execute('INSERT INTO order_items (order_id, dish_id, quantity, price) VALUES (?, ?, ?, ?)',
                   (order_id, dish['id'], dish['quantity'], dish['price']))
        total_amount += dish['quantity'] * dish['price']
    
    db.execute('UPDATE orders SET total_amount = ? WHERE id = ?', (total_amount, order_id))
    db.commit()

    return jsonify({'success': True})


@orders_bp.route('/orders/<int:order_id>', methods=['GET'])
@login_required
def get_order(order_id):
    db = get_db()
    orders = db.execute('SELECT id, table_number, order_time, status, total_amount FROM orders WHERE status = ? ORDER BY order_time', ('Pendiente',)).fetchall()
    order_dict = {order[0]: index + 1 for index, order in enumerate(orders)}
    order = db.execute('SELECT id, table_number, order_time, status, total_amount, payment_amount, change_amount FROM orders WHERE id = ?', (order_id,)).fetchone()
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    items = db.execute('SELECT dish_id, quantity, price FROM order_items WHERE order_id = ?', (order_id,)).fetchall()
    order_items = []
    for item in items:
        dish = db.execute('SELECT name FROM dishes WHERE id = ?', (item[0],)).fetchone()
        order_items.append({
            'name': dish[0],
            'quantity': item[1],
            'price': item[2]
        })
    order_data = {
        'id': order[0],
        'table_number': order[1],
        'order_time': order[2],
        'status': order[3],
        'total_amount': order[4],
        'items': order_items,
        'priority': order_dict.get(order[0], 1),
        'payment_amount': order[5],
        'change': order[6]
    }
    return jsonify(order_data)


@orders_bp.route('/orders/complete', methods=['POST'])
@login_required
def complete_order():
    db = get_db()
    data = request.get_json()
    order_id = data['order_id']
    payment_amount = float(data['payment_amount'])
    
    
    
    order = db.execute('SELECT id, table_number, order_time, total_amount FROM orders WHERE id = ?', (order_id,)).fetchone()
    items = db.execute('SELECT dish_id, quantity, price FROM order_items WHERE order_id = ?', (order_id,)).fetchall()
    order_items = []
    for item in items:
        dish = db.execute('SELECT name FROM dishes WHERE id = ?', (item[0],)).fetchone()
        order_items.append({
            'name': dish[0],
            'quantity': item[1],
            'price': item[2]
        })
    
    total_amount = order[3]
    change = payment_amount - total_amount

    db.execute('UPDATE orders SET status = ?, payment_amount = ?, change_amount = ? WHERE id = ?', 
               ('Pagado', payment_amount, payment_amount - total_amount, order_id))
    db.commit()
    
    ticket_content = {
        'table_number': order[1],
        'order_time': order[2],
        'total_amount': total_amount,
        'items': order_items,
        'payment_amount': payment_amount,
        'change': change
    }
    
    return jsonify({'success': True, 'ticket_content': ticket_content})


@orders_bp.route('/orders/update_status', methods=['POST'])
@login_required
def update_order_status():
    db = get_db()
    data = request.get_json()
    order_id = data['order_id']
    
    db.execute('UPDATE orders SET status = ? WHERE id = ?', ('Completo', order_id))
    db.commit()
    
    return jsonify({'success': True})
