from flask import Flask, g, render_template, session, jsonify
import sqlite3
from routes.users import users_bp
from routes.auth import auth_bp
from routes.orders import orders_bp
from routes.kitchen import kitchen_bp
from routes.cashier import cashier_bp
from routes.dishes import dishes_bp
from routes.decorators import login_required

app = Flask(__name__)
app.secret_key = 'f8da8eb2a7412a5d67d91d8f15e4ab169812b8b4700f0af6761956774a4f8c2a'

app.register_blueprint(users_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(orders_bp)
app.register_blueprint(kitchen_bp)
app.register_blueprint(cashier_bp)
app.register_blueprint(dishes_bp)

DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
@login_required
def dashboard():
    db = get_db()
    
    daily_sales = db.execute('''
        SELECT DATE(order_time) as date, SUM(total_amount) as total_sales 
        FROM orders 
        WHERE status = 'Pagado' 
        GROUP BY DATE(order_time)
        ORDER BY DATE(order_time)
    ''').fetchall()

    daily_sales = [{'date': row[0], 'total_sales': row[1]} for row in daily_sales]

    users = db.execute('SELECT id, first_name, last_name, email FROM users').fetchall()
    users = [{'id': row[0], 'first_name': row[1], 'last_name': row[2], 'email': row[3]} for row in users]

    dishes = db.execute('SELECT id, name, price FROM dishes').fetchall()
    dishes = [{'id': row[0], 'name': row[1], 'price': row[2]} for row in dishes]

    return render_template('index.html', daily_sales=daily_sales, users=users, dishes=dishes)



if __name__ == '__main__':
    app.run(debug=True)
