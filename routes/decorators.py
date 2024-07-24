from functools import wraps
from flask import redirect, url_for, session

def login_required(f):
    """
    Decorador para asegurar que una ruta solo puede ser accedida si el usuario está autenticado.
    
    :param f: La función a decorar.
    :return: La función decorada que redirige a la página de login si el usuario no está autenticado.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        """
        Función decorada que verifica si el usuario está autenticado.
        
        :param args: Argumentos posicionales.
        :param kwargs: Argumentos con nombre.
        :return: La función original si el usuario está autenticado, de lo contrario redirige a la página de login.
        """
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
