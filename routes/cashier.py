from flask import Blueprint, render_template, g, request, jsonify
import sqlite3
from .decorators import login_required

cashier_bp = Blueprint('cashier', __name__)

DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@cashier_bp.route('/cashier')
@login_required
def cashier():
    db = get_db()
    orders = db.execute('SELECT * FROM orders ORDER BY order_time').fetchall()
    orders_with_items = []
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
            'items': order_items
        })
    return render_template('cashier.html', orders=orders_with_items)

@cashier_bp.route('/orders/<int:order_id>', methods=['GET'])
@login_required
def get_order(order_id):
    db = get_db()
    order = db.execute('SELECT id, table_number, order_time, status, total_amount FROM orders WHERE id = ?', (order_id,)).fetchone()
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
        'items': order_items
    }
    return jsonify(order_data)

@cashier_bp.route('/orders/complete', methods=['POST'])
@login_required
def complete_order():
    db = get_db()
    data = request.get_json()
    order_id = data['order_id']
    payment_amount = float(data['payment_amount'])
    
    db.execute('UPDATE orders SET status = ? WHERE id = ?', ('Pagado', order_id))
    db.commit()
    
    # Generar el contenido del ticket
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
    
    ticket_content = {
        'table_number': order[1],
        'order_time': order[2],
        'total_amount': total_amount,
        'items': order_items,
        'payment_amount': payment_amount,
        'change': change
    }
    
    return jsonify({'success': True, 'ticket_content': ticket_content})
    