#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path
#import shutil
def run_command(command, project_path, shell=True):
    """
    Выполняет команду в командной строке и обрабатывает ошибки
    command - список аргументов команды (например, ["git", "init"])
    shell - использовать ли shell для выполнения (True/False)
    """
    try:
        # Выполняем команду и перехватываем вывод
        result = subprocess.run(
            command, 
            shell=shell, 
            check=True,           # Вызывать исключение при ошибке
            capture_output=True,  # Перехватывать вывод команды
            text=True,            # Возвращать строки вместо байтов
            encoding='cp866'      # Кодировка для русских символов в Windows
        )
        # Если команда выполнилась успешно, выводим сообщение
        print(f"✓ Успешно: {' '.join(command)}")
        return result.stdout      # Возвращаем то, что команда напечатала
    except subprocess.CalledProcessError as e:
        # Если команда завершилась с ошибкой
        print(f"✗ Ошибка в команде: {' '.join(command)}")
        print(f"Текст ошибки: {e.stderr}")

        # if project_path.exists():
        #     shutil.rmtree(project_path)
        #     #run_command(["rmdir", "/s"], project_path)
        # sys.exit(1)  # Завершаем программу с кодом ошибки

         # Выходим из папки проекта перед удалением
        original_dir = os.getcwd()
        if os.getcwd() == str(project_path):
            os.chdir("..")  # Выходим на уровень выше
            #print("Выходим из папки проекта ", os.getcwd())
        # Даем время системе освободить ресурсы
        import time
        time.sleep(1)
        
        # Удаляем папку проекта
        if project_path.exists():
            try:
                # Пробуем несколько раз с задержкой
                for attempt in range(3):
                    try:
                        #shutil.rmtree(project_path)
                        subprocess.run(["rmdir", "/s", "/q", str(project_path)], shell=True, check=False)
                        print(f"✓ Удалена папка проекта: {project_path}")
                        break
                    except PermissionError:
                        if attempt < 2:  # Если не последняя попытка
                            print(f"⚠ Попытка {attempt + 1}: Папка занята, ждем...")
                            time.sleep(2)  # Ждем 2 секунды
                        else:
                            print(f"⚠ Не удалось удалить папку {project_path} после 3 попыток")
                            print("Удалите папку вручную")
            except Exception as e:
                print(f"⚠ Ошибка при удалении: {e}")
                print("Удалите папку вручную")
        print("")
        sys.exit(1)

def create_project(github_url, project_name, project_path, creat_venv):
    """
    Основная функция создания проекта
    github_url - ссылка на GitHub репозиторий
    """
    
    # Извлекаем имя проекта из URL GitHub
    # Разбиваем URL по слешам, берем последнюю часть, убираем .git если есть
    # project_name = github_url.rstrip('/').split('/')[-1].replace('.git', '')
    
    # Выводим информационное сообщение
    print(f"🚀 Создаем проект: {project_name}")
    print("=" * 50)  # Рисуем разделитель из 50 знаков =
    
    # Проверяем, не существует ли уже папка с таким именем
    if project_path.exists():
        print(f"✗ Ошибка: Папка {project_name} уже существует!")
        sys.exit(1)  # Выходим с ошибкой
    
    # Создаем папку проекта
    project_path.mkdir()
    # Переходим в созданную папку
    os.chdir(project_path)
    print(f"✓ Создана папка проекта: {project_name}")
        # Инициализируем Git репозиторий
    run_command(["git", "init"], project_path)
    
    # Содержимое файла .gitignore - что Git должен игнорировать
    gitignore_content = """# Виртуальное окружение Python
venv/
.venv/

# Кэш Python
__pycache__/
*.pyc
*.pyo
*.pyd

# Файлы с переменными окружения
.env
.env.local

# Настройки редакторов кода
.vscode/
.idea/
*.swp
*.swo

# Системные файлы
.DS_Store
Thumbs.db
"""
    # Создаем и записываем файл .gitignore
    with open('.gitignore', 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    print("✓ Создан файл .gitignore")
    
    # Создаем виртуальное окружение Python
    if creat_venv:
        run_command(["python", "-m", "venv", "venv"], project_path)
        print("✓ Создано виртуальное окружение 'venv'")
    
    # Создаем базовую структуру папок проекта
    Path("src").mkdir()  # Папка для исходного кода
    (Path("src") / "__init__.py").touch()  # Пустой файл, чтобы Python видел папку как пакет
    print("✓ Создана структура папок")
    # Создаем README.md файл с описанием проекта
    readme_content = f"""
Описание вашего проекта{project_name}.

Установка и настройка.
.....
.....
..
"""
   # Записываем README.md файл
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
        print("✓ Создан файл README.md")

    
    # Создаем основной Python файл проекта
    main_content = """#!/usr/bin/env python3

def main():
    print("Hello, World!")


if __name__ == "__main__":
    main()"""

    # Записываем main.py файл
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(main_content)
        print("✓ Создан основной файл main.py")

    run_command(["git","add","."], project_path)
   
    run_command(["git","commit","-m", '"Первый коммит"'], project_path)
    
    run_command(["git", "remote", "add", "origin", github_url], project_path)
    run_command(["git", "branch", "-M", "main"], project_path)
    run_command(["git", "push", "-u", "origin", "main"], project_path)
    print("✓ Успешно: связан с удаленым репозиторием на GitHube и запушен")
    # run_command([r"venv\Scripts\activate"])
    
    print("=" * 50)
    print(r"""
Теперь все в ваших руках!!!
Активируйте виртуальное окружение [venv\Scripts\activate] 
Установите необходимые библиотеки для вашего проекта [pip install name lib1, lib2, ...]
Создайте файл requirements.txt [pip freeze > requirements.txt]
Добавте все в Git [git add.]
Не забывайте своевременно коммитеть и пушить изменение на сервер GitHub""")
    

def incorect_argv():
    print("Использование: python new_repo.py <github_repo_url> <-V>")
    print("Пример1: python new_repo.py https://github.com/username/repo-name.git")
    print("Пример2: python new_repo.py https://github.com/username/repo-name.git -V, создает дополнительно виртуальное окружение venv для python")
    sys.exit(1)

def main():
    # Указываем конкретную папку для проектов
    projects_folder = r"C:\Users\User\PyProject"  # r перед строкой - raw string, игнорировать esc последовательност
    creat_venv = False
    if len(sys.argv) < 2:
       incorect_argv()
    if len(sys.argv) >= 2 and len(sys.argv) <= 3:
        github_url = sys.argv[1]
        if not github_url.startswith('https://github.com/'):
            print("Ошибка: URL должен начинаться с https://github.com/")
            sys.exit(1)
        if len(sys.argv) == 3:
            if  sys.argv[2] == "-V":
                creat_venv = True
            else:
                incorect_argv()       
        # Извлекаем имя проекта из URL GitHub
        # Разбиваем URL по слешам, берем последнюю часть, убираем .git если есть
        project_name = github_url.rstrip('/').split('/')[-1].replace('.git', '')
        # Создаем объект Path для работы с путями
        project_path = Path(projects_folder) / project_name
        create_project(github_url, project_name, project_path, creat_venv)


if __name__ == "__main__":
    main()