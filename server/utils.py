import os
import hashlib
import shutil
from datetime import datetime

def get_repo_storage_path(repo_id, base_path='storage/repos'):
    """Получить путь к папке репозитория"""
    return os.path.join(base_path, str(repo_id))

def get_repo_file_path(repo_id, filepath, base_path='storage/repos'):
    """Получить полный путь к файлу репозитория"""
    repo_path = get_repo_storage_path(repo_id, base_path)
    return os.path.join(repo_path, filepath)

def create_repo_directory(repo_id, base_path='storage/repos'):
    """Создать папку для репозитория"""
    repo_path = get_repo_storage_path(repo_id, base_path)
    os.makedirs(repo_path, exist_ok=True)
    return repo_path

def calculate_file_hash(content):
    """Рассчитать хэш содержимого файла"""
    return hashlib.sha256(content).hexdigest()

def save_file_to_repo(repo_id, filepath, content, base_path='storage/repos'):
    """Сохранить файл в репозитории"""
    repo_path = create_repo_directory(repo_id, base_path)
    full_path = os.path.join(repo_path, filepath)
    
    # Создаем папки если нужно
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    # Сохраняем файл
    with open(full_path, 'wb') as f:
        f.write(content)
    
    return full_path

def read_file_from_repo(repo_id, filepath, base_path='storage/repos'):
    """Прочитать файл из репозитория"""
    full_path = get_repo_file_path(repo_id, filepath, base_path)
    
    if not os.path.exists(full_path):
        return None
    
    with open(full_path, 'rb') as f:
        return f.read()

def delete_file_from_repo(repo_id, filepath, base_path='storage/repos'):
    """Удалить файл из репозитория"""
    full_path = get_repo_file_path(repo_id, filepath, base_path)
    
    if os.path.exists(full_path):
        if os.path.isdir(full_path):
            shutil.rmtree(full_path)
        else:
            os.remove(full_path)
        return True
    return False

def scan_repo_directory(repo_id, base_path='storage/repos'):
    """Сканировать папку репозитория и вернуть структуру файлов"""
    repo_path = get_repo_storage_path(repo_id, base_path)
    
    if not os.path.exists(repo_path):
        return []
    
    files = []
    
    for root, dirs, filenames in os.walk(repo_path):
        # Папки
        for dirname in dirs:
            rel_path = os.path.relpath(os.path.join(root, dirname), repo_path)
            files.append({
                'name': dirname,
                'path': rel_path,
                'type': 'directory',
                'size': 0
            })
        
        # Файлы
        for filename in filenames:
            full_path = os.path.join(root, filename)
            rel_path = os.path.relpath(full_path, repo_path)
            size = os.path.getsize(full_path)
            
            files.append({
                'name': filename,
                'path': rel_path,
                'type': 'file',
                'size': size
            })
    
    return files

def create_initial_readme(repo_id, repo_name, description, base_path='storage/repos'):
    """Создать начальный README.md файл"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    description_text = description if description else 'Описание проекта'
    
    readme_content = f"# {repo_name}\n\n"
    readme_content += f"{description_text}\n\n"
    readme_content += "## Начало работы\n\n"
    readme_content += "Этот проект был создан в системе SCVP (Save and Control Version Project).\n\n"
    readme_content += "## Использование\n\n"
    readme_content += "Для работы с этим репозиторием используйте CLI команды:\n\n"
    readme_content += "```bash\n"
    readme_content += "scvp init .\n"
    readme_content += "scvp commit -m \"Ваши изменения\"\n"
    readme_content += "scvp push\n"
    readme_content += "```\n\n"
    readme_content += "## Автор\n\n"
    readme_content += "Репозиторий создан через веб-интерфейс SCVP.\n\n"
    readme_content += "---\n"
    readme_content += f"*Создано с помощью SCVP - {now}*\n"
    
    save_file_to_repo(repo_id, 'README.md', readme_content.encode('utf-8'), base_path)