from flask import Blueprint, render_template, g
import sqlite3
from .decorators import login_required

class KitchenRoutes:
    def __init__(self, app):
        """
        Inicializa el blueprint de cocina y configura la base de datos.
        
        :param app: La instancia de la aplicación Flask.
        """
        self.blueprint = Blueprint('kitchen', __name__)
        self.app = app
        self.DATABASE = 'database.db'
        self.setup_routes()

    def setup_routes(self):
        """
        Configura las rutas para la cocina.
        """
        self.blueprint.route('/kitchen')(self.kitchen)

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
    def kitchen(self):
        """
        Maneja la lógica para la página de la cocina, recuperando todos los pedidos
        pendientes y los detalles de los artículos asociados a cada pedido.
        
        :return: Renderiza la plantilla 'kitchen.html' con los datos de los pedidos pendientes.
        """
        db = self.get_db()
        orders = db.execute('SELECT * FROM orders WHERE status = ? ORDER BY order_time', ('Pendiente',)).fetchall()
        orders_with_items = []
        priority = 1
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
                'items': order_items,
                'priority': priority  
            })
            priority += 1
        return render_template('kitchen.html', orders=orders_with_items)
