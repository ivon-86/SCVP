from server import create_app, db
import os

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Создаём папку для хранения если её нет
        os.makedirs('storage', exist_ok=True)
        
        # Создаём таблицы в базе данных
        db.create_all()
        print("✅ База данных инициализирована")
        print("✅ Таблицы созданы")
    
    print("🚀 Запуск SCVP сервера...")
    print("📡 Сервер доступен по адресу: http://localhost:5000")
    print("🛑 Для остановки нажмите Ctrl+C")
    app.run(host='0.0.0.0', port=5000, debug=True)