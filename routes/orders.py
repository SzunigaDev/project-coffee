from flask import Blueprint, render_template, request, g, jsonify, session
import sqlite3
from datetime import datetime
from .decorators import login_required

class OrdersRoutes:
    def __init__(self, app):
        self.blueprint = Blueprint('orders', __name__)
        self.app = app
        self.DATABASE = 'database.db'
        self.setup_routes()

    def setup_routes(self):
        self.blueprint.route('/orders', methods=['GET', 'POST'])(self.orders)
        self.blueprint.route('/orders/create', methods=['POST'])(self.create_order)
        self.blueprint.route('/orders/<int:order_id>', methods=['GET'])(self.get_order)
        self.blueprint.route('/orders/complete', methods=['POST'])(self.complete_order)
        self.blueprint.route('/orders/update_status', methods=['POST'])(self.update_order_status)

    def get_db(self):
        if not hasattr(g, '_database'):
            g._database = sqlite3.connect(self.DATABASE)
            g._database.row_factory = sqlite3.Row
        return g._database

    @login_required
    def orders(self):
        db = self.get_db()
        orders = db.execute('SELECT * FROM orders').fetchall()
        dishes = db.execute('SELECT * FROM dishes').fetchall()
        return render_template('orders.html', orders=orders, dishes=dishes)

    @login_required
    def create_order(self):
        db = self.get_db()
        data = request.get_json()
        table_number = data['table_number']
        dishes = data['dishes']
        order_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        db.execute('INSERT INTO orders (table_number, order_time, status, total_amount, payment_amount, change_amount) VALUES (?, ?, ?, ?, ?, ?)', 
                   (table_number, order_time, 'Pendiente', 0, 0, 0))
        order_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]

        total_amount = 0
        for dish in dishes:
            db.execute('INSERT INTO order_items (order_id, dish_id, quantity, price) VALUES (?, ?, ?, ?)',
                       (order_id, dish['id'], dish['quantity'], dish['price']))
            total_amount += dish['quantity'] * dish['price']
        
        db.execute('UPDATE orders SET total_amount = ? WHERE id = ?', (total_amount, order_id))
        db.commit()

        return jsonify({'success': True})

    @login_required
    def get_order(self, order_id):
        db = self.get_db()
        orders = db.execute('SELECT id, table_number, order_time, status, total_amount FROM orders WHERE status = ? ORDER BY order_time', ('Pendiente',)).fetchall()
        order_dict = {order['id']: index + 1 for index, order in enumerate(orders)}
        order = db.execute('SELECT id, table_number, order_time, status, total_amount, payment_amount, change_amount FROM orders WHERE id = ?', (order_id,)).fetchone()
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        items = db.execute('SELECT dish_id, quantity, price FROM order_items WHERE order_id = ?', (order_id,)).fetchall()
        order_items = []
        for item in items:
            dish = db.execute('SELECT name FROM dishes WHERE id = ?', (item['dish_id'],)).fetchone()
            order_items.append({
                'name': dish['name'],
                'quantity': item['quantity'],
                'price': item['price']
            })
        
        user_name = db.execute('SELECT first_name, last_name FROM users WHERE id = ?', (session.get('user_id'),)).fetchone()
        full_user_name = f"{user_name['first_name']} {user_name['last_name']}"

        order_data = {
            'id': order['id'],
            'table_number': order['table_number'],
            'order_time': order['order_time'],
            'status': order['status'],
            'total_amount': order['total_amount'],
            'items': order_items,
            'priority': order_dict.get(order['id'], 1),
            'payment_amount': order['payment_amount'],
            'change': order['change_amount'],
            'user_id': full_user_name
        }
        return jsonify(order_data)

    @login_required
    def complete_order(self):
        db = self.get_db()
        data = request.get_json()
        order_id = data['order_id']
        payment_amount = float(data['payment_amount'])
        
        order = db.execute('SELECT id, table_number, order_time, total_amount FROM orders WHERE id = ?', (order_id,)).fetchone()
        items = db.execute('SELECT dish_id, quantity, price FROM order_items WHERE order_id = ?', (order_id,)).fetchall()
        order_items = []
        for item in items:
            dish = db.execute('SELECT name FROM dishes WHERE id = ?', (item['dish_id'],)).fetchone()
            order_items.append({
                'name': dish['name'],
                'quantity': item['quantity'],
                'price': item['price']
            })
        
        total_amount = order['total_amount']
        change = payment_amount - total_amount

        print(f"Total amount: {total_amount}, Change: {change}")

        db.execute('UPDATE orders SET status = ?, payment_amount = ?, change_amount = ? WHERE id = ?', 
                   ('Pagado', payment_amount, change, order_id))
        db.commit()
        
        user_name = db.execute('SELECT first_name, last_name FROM users WHERE id = ?', (session.get('user_id'),)).fetchone()
        full_user_name = f"{user_name['first_name']} {user_name['last_name']}"

        ticket_content = {
            'table_number': order['table_number'],
            'order_time': order['order_time'],
            'total_amount': total_amount,
            'items': order_items,
            'payment_amount': payment_amount,
            'change_amount': change,
            'user_name': full_user_name
        }

        print(f"Ticket content: {ticket_content}")
        
        return jsonify({'success': True, 'ticket_content': ticket_content})


    @login_required
    def update_order_status(self):
        db = self.get_db()
        data = request.get_json()
        order_id = data['order_id']
        
        db.execute('UPDATE orders SET status = ? WHERE id = ?', ('Completo', order_id))
        db.commit()
        
        return jsonify({'success': True})
