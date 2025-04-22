import os
from dotenv import load_dotenv
from pathlib import Path  # Para manejo moderno de rutas

# Cargar variables de entorno desde .env en el directorio base
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    # Configuración básica
    SECRET_KEY = os.getenv('SECRET_KEY', 'clave-secreta-por-defecto-solo-para-desarrollo')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'clave-jwt-secreta-por-defecto-solo-para-desarrollo')
    
    # Configuración de base de datos con validación
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST')
    DB_NAME = os.getenv('DB_NAME')
    
    if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_NAME]):
        raise ValueError("Faltan variables de configuración de la base de datos")
    
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración JWT adicional recomendada
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))  # 1 hora por defecto
    PROPAGATE_EXCEPTIONS = True  # Para mejor manejo de errores

    @classmethod
    def validate_config(cls):
        """Valida que las configuraciones críticas estén presentes"""
        required_keys = ['SECRET_KEY', 'JWT_SECRET_KEY']
        for key in required_keys:
            if not getattr(cls, key) or getattr(cls, key).startswith('clave-'):
                raise ValueError(f"Configuración inválida o faltante para {key}")

# Validar la configuración al importar
Config.validate_config()