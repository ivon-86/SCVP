import os
from datetime import timedelta

class Config:
    # Базовые настройки
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # База данных
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///scvp.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Сессии
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Загрузка файлов
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'storage'
    
    # Тема по умолчанию
    DEFAULT_THEME = 'light'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}