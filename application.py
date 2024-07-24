from flask import Flask, g, render_template, session, jsonify
import sqlite3
from routes.auth       import AuthRoutes
from routes.cashier    import CashierRoutes
from routes.dishes     import DishesRoutes
from routes.kitchen    import KitchenRoutes
from routes.orders     import OrdersRoutes
from routes.users      import UsersRoutes
from routes.decorators import login_required

class App:
    def __init__(self):
        """
        Inicializa la aplicación Flask, configura la clave secreta y la base de datos,
        y registra los blueprints de las rutas.
        """
        self.app = Flask(__name__)
        self.app.secret_key = 'f8da8eb2a7412a5d67d91d8f15e4ab169812b8b4700f0af6761956774a4f8c2a'
        self.app.config['DATABASE'] = 'database.db'
        self.register_blueprints()
        self.setup_database()

    def register_blueprints(self):
        """
        Registra los blueprints de las rutas para las diferentes secciones de la aplicación.
        """
        self.app.register_blueprint(AuthRoutes(self.app).blueprint)
        self.app.register_blueprint(CashierRoutes(self.app).blueprint)
        self.app.register_blueprint(DishesRoutes(self.app).blueprint)
        self.app.register_blueprint(KitchenRoutes(self.app).blueprint)
        self.app.register_blueprint(OrdersRoutes(self.app).blueprint)
        self.app.register_blueprint(UsersRoutes(self.app).blueprint)

    def setup_database(self):
        """
        Configura la conexión a la base de datos y la ruta principal de la aplicación.
        """
        self.app.teardown_appcontext(self.close_connection)
        self.app.route('/')(self.dashboard)

    def get_db(self):
        """
        Obtiene una conexión a la base de datos SQLite. Si no existe una conexión activa,
        se crea una nueva.
        """
        if not hasattr(g, '_database'):
            g._database = sqlite3.connect(self.app.config['DATABASE'])
            g._database.row_factory = sqlite3.Row
        return g._database

    def close_connection(self, exception):
        """
        Cierra la conexión a la base de datos al finalizar el contexto de la aplicación.
        """
        db = g.pop('_database', None)
        if db is not None:
            db.close()

    @login_required
    def dashboard(self):
        """
        Ruta principal de la aplicación que muestra el tablero de control. 
        Requiere que el usuario esté autenticado.
        """
        db = self.get_db()
        
        daily_sales = db.execute('''
            SELECT DATE(order_time) as date, SUM(total_amount) as total_sales 
            FROM orders 
            WHERE status = 'Pagado' 
            GROUP BY DATE(order_time)
            ORDER BY DATE(order_time)
        ''').fetchall()

        daily_sales = [{'date': row['date'], 'total_sales': row['total_sales']} for row in daily_sales]

        users = db.execute('SELECT id, first_name, last_name, email FROM users').fetchall()
        users = [{'id': row['id'], 'first_name': row['first_name'], 'last_name': row['last_name'], 'email': row['email']} for row in users]

        dishes = db.execute('SELECT id, name, price FROM dishes').fetchall()
        dishes = [{'id': row['id'], 'name': row['name'], 'price': row['price']} for row in dishes]

        return render_template('index.html', daily_sales=daily_sales, users=users, dishes=dishes)

    def run(self):
        """
        Ejecuta la aplicación Flask en modo debug.
        """
        self.app.run(debug=True)

if __name__ == '__main__':
    """
    Punto de entrada principal de la aplicación.
    """
    app_instance = App()
    app_instance.run()
