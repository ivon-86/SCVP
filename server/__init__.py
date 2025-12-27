from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Создаём экземпляры расширений
db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Загружаем конфигурацию
    from .config import config
    app.config.from_object(config[config_name])
    
    # Инициализируем расширения
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Пожалуйста, войдите в систему'
    
    # Импортируем User здесь, после инициализации db
    with app.app_context():
        from .models import User
        
        # Определяем user_loader внутри контекста приложения
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))
    
    # Регистрируем blueprints
    from .routes.main import main as main_blueprint
    from .routes.auth import auth as auth_blueprint
    
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    return app