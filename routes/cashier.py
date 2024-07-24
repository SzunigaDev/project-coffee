from flask import Blueprint, render_template, g, request, jsonify, session
import sqlite3
from .decorators import login_required

class CashierRoutes:
    def __init__(self, app):
        self.blueprint = Blueprint('cashier', __name__)
        self.app = app
        self.DATABASE = 'database.db'
        self.setup_routes()

    def setup_routes(self):
        self.blueprint.route('/cashier')(self.cashier)
        self.blueprint.route('/orders/<int:order_id>', methods=['GET'])(self.get_order)
        self.blueprint.route('/orders/complete', methods=['POST'])(self.complete_order)

    def get_db(self):
        if not hasattr(g, '_database'):
            g._database = sqlite3.connect(self.DATABASE)
            g._database.row_factory = sqlite3.Row
        return g._database

    @login_required
    def cashier(self):
        db = self.get_db()
        orders = db.execute('SELECT * FROM orders ORDER BY order_time').fetchall()
        orders_with_items = []
        for order in orders:
            items = db.execute('SELECT dish_id, quantity, price FROM order_items WHERE order_id = ?', (order['id'],)).fetchall()
            order_items = []
            for item in items:
                dish = db.execute('SELECT name FROM dishes WHERE id = ?', (item['dish_id'],)).fetchone()
                order_items.append({
                    'name': dish['name'],
                    'quantity': item['quantity'],
                    'price': item['price']
                })
            orders_with_items.append({
                'id': order['id'],
                'table_number': order['table_number'],
                'order_time': order['order_time'],
                'status': order['status'],
                'total_amount': order['total_amount'],
                'items': order_items
            })
        return render_template('cashier.html', orders=orders_with_items)

    @login_required
    def get_order(self, order_id):
        db = self.get_db()
        order = db.execute('SELECT id, table_number, order_time, status, total_amount, payment_amount, change_amount FROM orders WHERE id = ?', (order_id,)).fetchone()
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
            'payment_amount': order['payment_amount'],
            'change_amount': order['change_amount'],
            'user_name': full_user_name
        }
        return jsonify(order_data)

    @login_required
    def complete_order(self):
        db = self.get_db()
        data = request.get_json()
        order_id = data['order_id']
        payment_amount = float(data['payment_amount'])
        
        order = db.execute('SELECT id, table_number, order_time, total_amount, payment_amount, change_amount FROM orders WHERE id = ?', (order_id,)).fetchone()
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
            'payment_amount': order['payment_amount'],
            'change_amount': order['change_amount'],
            'user_name': full_user_name
        }

        print(f"Ticket content: {ticket_content}")
        
        return jsonify({'success': True, 'ticket_content': ticket_content})

