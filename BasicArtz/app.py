from flask import Flask
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Inicializar la app y extensiones
app = Flask(__name__)
bcrypt = Bcrypt(app)

# Configuración de la aplicación usando variables de entorno
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com') 
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 465))
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
mail = Mail(app)

# Importar y registrar rutas
from routes.admin_routes import *
from routes.user_routes import *
from routes.carrito_routes import *
from routes.categorias_routes import *
from routes.general_routes import *

if __name__ == '__main__':
    app.run(debug=True)
