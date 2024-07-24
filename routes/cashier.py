from flask import Blueprint, render_template, g, request, jsonify, session
import sqlite3
from .decorators import login_required

class CashierRoutes:
    def __init__(self, app):
        """
        Inicializa el blueprint de cajero y configura la base de datos.
        
        :param app: La instancia de la aplicación Flask.
        """
        self.blueprint = Blueprint('cashier', __name__)
        self.app = app
        self.DATABASE = 'database.db'
        self.setup_routes()

    def setup_routes(self):
        """
        Configura las rutas para el cajero.
        """
        self.blueprint.route('/cashier')(self.cashier)
        self.blueprint.route('/cashier/group_orders', methods=['POST'])(self.group_orders)

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

    @login_required
    def cashier(self):
        """
        Maneja la lógica para la página del cajero, recuperando todos los pedidos
        y los detalles de los artículos asociados a cada pedido.
        
        :return: Renderiza la plantilla 'cashier.html' con los datos de los pedidos.
        """
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
    def group_orders(self):
        """
        Agrupa todas las órdenes para una mesa específica.
        
        :return: Devuelve un JSON con las órdenes agrupadas y el total.
        """
        data = request.get_json()
        table_number = data['table_number']

        db = self.get_db()
        grouped_orders = db.execute('SELECT * FROM orders WHERE table_number = ? AND status != ?', (table_number, 'Pagado')).fetchall()

        total_amount = 0
        orders_with_items = []
        for order in grouped_orders:
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
            total_amount += order['total_amount']

        return jsonify({'grouped_orders': orders_with_items, 'total_amount': total_amount})
