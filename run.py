from server import create_app, db
import os

# Создаём приложение
app = create_app()

# Создаём таблицы и выполняем инициализацию
with app.app_context():
    # Создаём папку для хранения если её нет
    os.makedirs('storage', exist_ok=True)
    
    # Создаём таблицы в базе данных
    db.create_all()
    
    # Проверяем, есть ли пользователи
    from server.models import User
    user_count = User.query.count()
    print(f"✅ База данных инициализирована")
    print(f"✅ Создано таблиц: 1 (users)")
    print(f"✅ Пользователей в базе: {user_count}")

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Запуск SCVP сервера...")
    print("📡 Сервер доступен по адресу: http://localhost:5000")
    print("📁 Главная страница: http://localhost:5000/")
    print("🔑 Страница входа: http://localhost:5000/auth/login")
    print("🚀 Регистрация: http://localhost:5000/auth/register")
    print("=" * 50)
    print("🛑 Для остановки нажмите Ctrl+C")
    app.run(host='0.0.0.0', port=5000, debug=True)