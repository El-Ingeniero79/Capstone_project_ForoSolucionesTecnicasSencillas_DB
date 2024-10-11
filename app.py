from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from models import db, bcrypt, User
from auth import auth_bp
from posts import posts_bp
from dotenv import load_dotenv
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

def create_app():
    app = Flask(__name__)
    
    CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
    
    app.config.from_object(Config)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

    # Inicialización de la base de datos
    db.init_app(app)  
    Migrate(app, db)
    bcrypt.init_app(app) 
    
    # Configuración JWT
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    JWTManager(app)

    # Registro de blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(posts_bp)

    return app

app = create_app()

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify({'message': f'Autenticado como el usuario {current_user}'}), 200

