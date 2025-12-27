from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Пожалуйста, войдите в систему'

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Загружаем конфигурацию
    from .config import config
    app.config.from_object(config[config_name])
    
    # Инициализируем расширения
    db.init_app(app)
    login_manager.init_app(app)
    
    # Импортируем модели после инициализации db
    with app.app_context():
        from . import models
    
    # Регистрируем blueprints
    from .routes import main, auth
    app.register_blueprint(main.main)
    app.register_blueprint(auth.auth, url_prefix='/auth')
    
    return app