@echo off
echo Создание структуры проекта SCVP...
echo.

REM Создаём основную структуру папок
echo Создание папок...
mkdir server 2>nul
mkdir server\static 2>nul
mkdir server\static\css 2>nul
mkdir server\static\fonts 2>nul
mkdir server\templates 2>nul
mkdir server\routes 2>nul

REM Создаём пустые файлы
echo Создание файлов...

REM Основные файлы Flask
type nul > server\__init__.py
type nul > server\app.py
type nul > server\config.py
type nul > server\models.py
type nul > server\auth.py
type nul > server\forms.py

REM Файлы маршрутов
type nul > server\routes\__init__.py
type nul > server\routes\main.py
type nul > server\routes\auth.py

REM HTML шаблоны
type nul > server\templates\layout.html
type nul > server\templates\index.html
type nul > server\templates\login.html
type nul > server\templates\register.html
type nul > server\templates\dashboard.html
type nul > server\templates\new_repo.html
type nul > server\templates\help.html
type nul > server\templates\about.html
type nul > server\templates\repo_view.html

REM CSS файлы
type nul > server\static\css\style.css
type nul > server\static\css\light.css
type nul > server\static\css\dark.css
type nul > server\static\fonts\monospace.css

REM Корневые файлы
type nul > requirements.txt
type nul > run.py
type nul > .gitignore

echo.
echo ✅ Структура проекта создана!
echo.
echo Список созданных папок и файлов:
echo.
dir /b server
echo.
dir /b server\static
echo.
dir /b server\templates
echo.
dir /b server\routes
echo.
echo Следующие шаги:
echo 1. Активируйте виртуальное окружение
echo 2. Установите Flask: pip install flask flask-login flask-sqlalchemy
echo 3. Заполните файлы кодом (будем делать по шагам)
echo.
pause