from flask import Flask
from flask_cors import CORS
from .config import Config
from .extensions import db, bcrypt, ma, jwt, migrate
from app.routes.availability_routes import availability_bp
from app.routes.subject_routes import subject_bp
from app.routes.load_routes    import load_bp
from app.routes.habit_routes import habit_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(availability_bp, url_prefix='/api')
    app.register_blueprint(subject_bp, url_prefix='/api')
    app.register_blueprint(load_bp,    url_prefix='/api')
    app.register_blueprint(habit_bp, url_prefix='/api')

    # Inicializar extensiones
    db.init_app(app)
    bcrypt.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)  # Inicializar Flask-Migrate
    CORS(app)

    # Importar modelos después de inicializar db
    from app.models.user import User
    from app.models.user_profile import UserProfile
    
    # Registrar blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.profile_routes import profile_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(profile_bp, url_prefix='/api')

    return app