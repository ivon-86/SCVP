from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/test-db')
def test_db():
    """Тестовый маршрут для проверки базы данных"""
    from server.models import User, db
    
    # Создаём тестового пользователя
    test_user = User(
        username='testuser',
        email='test@example.com',
        password_hash='test_hash'
    )
    
    try:
        db.session.add(test_user)
        db.session.commit()
        return "✅ Тестовый пользователь создан успешно!"
    except Exception as e:
        db.session.rollback()
        return f"❌ Ошибка: {str(e)}"