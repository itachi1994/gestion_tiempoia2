import os
from dotenv import load_dotenv
from pathlib import Path

# Cargar variables de entorno desde .env
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    # Configuración general
    SECRET_KEY = os.getenv('SECRET_KEY', 'clave-secreta-por-defecto-solo-para-desarrollo')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'clave-jwt-secreta-por-defecto-solo-para-desarrollo')

    # Configuración JWT
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 10800))  # 1 hora
    PROPAGATE_EXCEPTIONS = True

    # Configuración de la base de datos
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST')
    DB_NAME = os.getenv('DB_NAME')

    if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_NAME]):
        raise ValueError("Faltan variables de configuración de la base de datos")

    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuración de correo
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'gabrielvelilla.56@example.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '123456') 
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'gabrielvelilla.56@gmail.com')

    @classmethod
    def validate_config(cls):
        """Valida que las configuraciones críticas estén presentes"""
        required_keys = ['SECRET_KEY', 'JWT_SECRET_KEY']
        for key in required_keys:
            if not getattr(cls, key) or getattr(cls, key).startswith('clave-'):
                raise ValueError(f"Configuración inválida o faltante para {key}")


# Validar configuración al cargar
Config.validate_config()
