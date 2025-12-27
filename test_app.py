from server import create_app, db
from server.models import User

app = create_app()

with app.app_context():
    # Проверяем создание таблиц
    db.create_all()
    print("✅ Таблицы созданы")
    
    # Проверяем создание пользователя
    try:
        user = User(username='test', email='test@test.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        print("✅ Тестовый пользователь создан")
    except Exception as e:
        print(f"❌ Ошибка: {e}")