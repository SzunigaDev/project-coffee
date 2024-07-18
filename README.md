# Proyecto de Cafetería con Flask

Este proyecto es una aplicación web para la gestión de una cafetería, desarrollada con Flask. Incluye módulos para gestionar usuarios, pedidos, cocina y caja registradora.

## Instalación

1. Clonar el repositorio:

   ```sh
   git clone <URL_DEL_REPOSITORIO>
   cd nombre_del_proyecto
   ```

2. Crear un entorno virtual e instalar las dependencias:

   ```sh
   python -m venv venv
   source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. Inicializar la base de datos:

   ```sh
   python init_db.py
   ```

   **Nota:** El script `init_db.py` eliminará la base de datos existente y creará una nueva. Si deseas evitar que se elimine la base de datos existente, comenta las siguientes líneas en `init_db.py`:

   ```python
   import os

   DATABASE = 'database.db'
   # Eliminar la base de datos existente
   if os.path.exists(DATABASE):
       os.remove(DATABASE)
   ```

4. Ejecutar la aplicación:

   ```sh
   python app.py
   ```

5. Abrir en el navegador:
   ```sh
   http://127.0.0.1:5000/
   ```

## Usuarios Predeterminados

El script `init_db.py` crea dos usuarios predeterminados:

1. **Admin**

   - Nombre: Admin
   - Email: admin@mail.com
   - Contraseña: 1234

2. **Sergio Zuniga**
   - Nombre: Sergio
   - Apellido: Zuniga
   - Email: szuniga@mail.com
   - Contraseña: 123456789

## Funcionalidades

- **Usuarios:** Gestión de usuarios.
- **Pedidos:** Creación y visualización de pedidos.
- **Cocina:** Gestión de pedidos en cocina.
- **Caja Registradora:** Cobro de pedidos y generación de tickets.

## Estructura del Proyecto

- `app.py`: Archivo principal de la aplicación.
- `init_db.py`: Script para inicializar la base de datos.
- `templates/`: Directorio de plantillas HTML.
- `static/`: Archivos estáticos como CSS y JavaScript.
- `routes/`: Blueprints de las rutas de la aplicación.

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.
