from flask import Blueprint, render_template, redirect, url_for, flash, request, session, send_file, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import hashlib
import io
from datetime import datetime

from server.forms import NewRepoForm, EditRepoForm, UploadFileForm, EditFileForm, NewFolderForm
from server.models import db, Repository, Commit
from server.utils import (
    create_repo_directory, save_file_to_repo, read_file_from_repo,
    delete_file_from_repo, scan_repo_directory, create_initial_readme
)

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/dashboard')
@login_required
def dashboard():
    """Панель управления - список репозиториев"""
    repos = Repository.query.filter_by(user_id=current_user.id).order_by(Repository.updated_at.desc()).all()
    return render_template('dashboard.html', repos=repos, show_sidebar=True)


@main.route('/new-repo', methods=['GET', 'POST'])
@login_required
def new_repo():
    """Создание нового репозитория"""
    form = NewRepoForm()
    
    if form.validate_on_submit():
        # Создаём репозиторий
        repo = Repository(
            name=form.name.data,
            description=form.description.data,
            user_id=current_user.id,
            is_public=form.is_public.data
        )
        
        try:
            db.session.add(repo)
            db.session.commit()
            
            # Создаём папку для репозитория
            create_repo_directory(repo.id)
            
            # Создаём начальный коммит
            commit_hash = hashlib.sha256(
                f"{repo.id}{datetime.utcnow().isoformat()}".encode()
            ).hexdigest()[:16]
            
            initial_commit = Commit(
                repo_id=repo.id,
                user_id=current_user.id,
                message="Initial commit",
                commit_hash=commit_hash,
                version_number=1
            )
            
            db.session.add(initial_commit)
            db.session.commit()
            
            # Создаём README.md если нужно
            if form.generate_readme.data:
                create_initial_readme(repo.id, repo.name, repo.description)
            
            flash(f'Репозиторий "{repo.name}" успешно создан!', 'success')
            return redirect(url_for('main.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при создании репозитория: {str(e)}', 'error')
    
    return render_template('new_repo.html', form=form)


@main.route('/toggle-theme')
def toggle_theme():
    """Переключение темы оформления"""
    current_theme = session.get('theme', 'light')
    new_theme = 'dark' if current_theme == 'light' else 'light'
    session['theme'] = new_theme
    
    # Сохраняем в профиль пользователя, если авторизован
    if current_user.is_authenticated:
        current_user.theme = new_theme
        db.session.commit()
        flash(f'Тема изменена на {new_theme}', 'info')
    
    # Возвращаем на предыдущую страницу или на главную
    return redirect(request.referrer or url_for('main.index'))


@main.route('/about')
def about():
    return render_template('about.html')


@main.route('/help')
def help():
    return render_template('help.html')


@main.route('/repo/<int:repo_id>')
@login_required
def repo_view(repo_id):
    """Просмотр репозитория"""
    repo = Repository.query.get_or_404(repo_id)
    
    # Проверяем права доступа
    if repo.user_id != current_user.id and not repo.is_public:
        flash('У вас нет доступа к этому репозиторию', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Сканируем файлы репозитория
    files = scan_repo_directory(repo_id)
    
    commits = Commit.query.filter_by(repo_id=repo_id).order_by(Commit.created_at.desc()).all()
    
    return render_template('repo_view.html', 
                          repo=repo, 
                          files=files,
                          commits=commits,
                          upload_form=UploadFileForm(),
                          folder_form=NewFolderForm())


@main.route('/repo/<int:repo_id>/upload', methods=['POST'])
@login_required
def upload_file(repo_id):
    """Загрузка файла в репозиторий"""
    repo = Repository.query.get_or_404(repo_id)
    
    # Проверяем права доступа
    if repo.user_id != current_user.id:
        flash('У вас нет прав для загрузки файлов в этот репозиторий', 'error')
        return redirect(url_for('main.repo_view', repo_id=repo_id))
    
    form = UploadFileForm()
    
    if form.validate_on_submit():
        file = form.file.data
        filepath = form.filepath.data or ''
        
        # Безопасное имя файла
        filename = secure_filename(file.filename)
        
        if filepath:
            full_path = os.path.join(filepath, filename)
        else:
            full_path = filename
        
        try:
            # Читаем содержимое файла
            content = file.read()
            
            # Сохраняем файл
            save_file_to_repo(repo_id, full_path, content)
            
            # Обновляем время репозитория
            repo.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Создаем коммит
            create_commit(repo_id, f"Добавлен файл: {filename}")
            
            flash(f'Файл "{filename}" успешно загружен!', 'success')
            
        except Exception as e:
            flash(f'Ошибка при загрузке файла: {str(e)}', 'error')
    
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Ошибка в поле {getattr(form, field).label.text}: {error}', 'error')
    
    return redirect(url_for('main.repo_view', repo_id=repo_id))


@main.route('/repo/<int:repo_id>/create-folder', methods=['POST'])
@login_required
def create_folder(repo_id):
    """Создание папки в репозитории"""
    repo = Repository.query.get_or_404(repo_id)
    
    # Проверяем права доступа
    if repo.user_id != current_user.id:
        flash('У вас нет прав для создания папок в этом репозитории', 'error')
        return redirect(url_for('main.repo_view', repo_id=repo_id))
    
    form = NewFolderForm()
    
    if form.validate_on_submit():
        folder_path = form.folder_path.data or ''
        folder_name = form.folder_name.data
        
        if folder_path:
            full_path = os.path.join(folder_path, folder_name)
        else:
            full_path = folder_name
        
        try:
            # Создаем папку
            repo_path = create_repo_directory(repo_id)
            folder_full_path = os.path.join(repo_path, full_path)
            os.makedirs(folder_full_path, exist_ok=True)
            
            # Обновляем время репозитория
            repo.updated_at = datetime.utcnow()
            db.session.commit()
            
            flash(f'Папка "{folder_name}" успешно создана!', 'success')
            
        except Exception as e:
            flash(f'Ошибка при создании папки: {str(e)}', 'error')
    
    return redirect(url_for('main.repo_view', repo_id=repo_id))


@main.route('/repo/<int:repo_id>/download/<path:filepath>')
@login_required
def download_file(repo_id, filepath):
    """Скачивание файла из репозитория"""
    repo = Repository.query.get_or_404(repo_id)
    
    # Проверяем права доступа
    if repo.user_id != current_user.id and not repo.is_public:
        abort(403)
    
    # Читаем файл
    content = read_file_from_repo(repo_id, filepath)
    
    if content is None:
        flash('Файл не найден', 'error')
        return redirect(url_for('main.repo_view', repo_id=repo_id))
    
    # Отправляем файл
    filename = os.path.basename(filepath)
    return send_file(
        io.BytesIO(content),
        download_name=filename,
        as_attachment=True
    )


@main.route('/repo/<int:repo_id>/delete/<path:filepath>')
@login_required
def delete_file(repo_id, filepath):
    """Удаление файла из репозитория"""
    repo = Repository.query.get_or_404(repo_id)
    
    # Проверяем права доступа
    if repo.user_id != current_user.id:
        flash('У вас нет прав для удаления файлов из этого репозитория', 'error')
        return redirect(url_for('main.repo_view', repo_id=repo_id))
    
    try:
        # Удаляем файл
        success = delete_file_from_repo(repo_id, filepath)
        
        if success:
            # Обновляем время репозитория
            repo.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Создаем коммит
            filename = os.path.basename(filepath)
            create_commit(repo_id, f"Удален файл: {filename}")
            
            flash(f'Файл "{filename}" успешно удален!', 'success')
        else:
            flash('Файл не найден', 'error')
            
    except Exception as e:
        flash(f'Ошибка при удалении файла: {str(e)}', 'error')
    
    return redirect(url_for('main.repo_view', repo_id=repo_id))


@main.route('/repo/<int:repo_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_repo(repo_id):
    """Редактирование репозитория"""
    repo = Repository.query.get_or_404(repo_id)
    
    # Проверяем права доступа
    if repo.user_id != current_user.id:
        flash('У вас нет прав для редактирования этого репозитория', 'error')
        return redirect(url_for('main.repo_view', repo_id=repo_id))
    
    form = EditRepoForm(obj=repo)
    
    if form.validate_on_submit():
        repo.name = form.name.data
        repo.description = form.description.data
        repo.is_public = form.is_public.data
        
        db.session.commit()
        flash('Репозиторий успешно обновлен!', 'success')
        return redirect(url_for('main.repo_view', repo_id=repo_id))
    
    return render_template('edit_repo.html', repo=repo, form=form)


@main.route('/repo/<int:repo_id>/delete-repo')
@login_required
def delete_repo(repo_id):
    """Удаление репозитория"""
    repo = Repository.query.get_or_404(repo_id)
    
    # Проверяем права доступа
    if repo.user_id != current_user.id:
        flash('У вас нет прав для удаления этого репозитория', 'error')
        return redirect(url_for('main.dashboard'))
    
    try:
        # Удаляем из базы данных
        db.session.delete(repo)
        db.session.commit()
        
        # Удаляем файлы репозитория
        import shutil
        repo_path = create_repo_directory(repo_id)
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)
        
        flash(f'Репозиторий "{repo.name}" успешно удален!', 'success')
        
    except Exception as e:
        flash(f'Ошибка при удалении репозитория: {str(e)}', 'error')
    
    return redirect(url_for('main.dashboard'))


@main.route('/repo/<int:repo_id>/edit-file/<path:filepath>', methods=['GET', 'POST'])
@login_required
def edit_file(repo_id, filepath):
    """Редактирование файла"""
    repo = Repository.query.get_or_404(repo_id)
    
    # Проверяем права доступа
    if repo.user_id != current_user.id:
        flash('У вас нет прав для редактирования файлов в этом репозитории', 'error')
        return redirect(url_for('main.repo_view', repo_id=repo_id))
    
    # Читаем текущее содержимое файла
    content = read_file_from_repo(repo_id, filepath)
    
    if content is None:
        flash('Файл не найден', 'error')
        return redirect(url_for('main.repo_view', repo_id=repo_id))
    
    form = EditFileForm()
    
    if form.validate_on_submit():
        # Сохраняем изменения
        new_content = form.content.data.encode('utf-8')
        save_file_to_repo(repo_id, filepath, new_content)
        
        # Обновляем время репозитория
        repo.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Создаем коммит
        create_commit(repo_id, f"Изменен файл: {os.path.basename(filepath)}")
        
        flash('Файл успешно сохранен!', 'success')
        return redirect(url_for('main.repo_view', repo_id=repo_id))
    
    # Заполняем форму текущим содержимым
    form.content.data = content.decode('utf-8', errors='ignore')
    form.filename.data = os.path.basename(filepath)
    
    return render_template('edit_file.html', repo=repo, filepath=filepath, form=form)


def create_commit(repo_id, message):
    """Создать коммит"""
    commit_hash = hashlib.sha256(
        f"{repo_id}{datetime.utcnow().isoformat()}{message}".encode()
    ).hexdigest()[:16]
    
    # Получаем последний коммит
    last_commit = Commit.query.filter_by(repo_id=repo_id).order_by(Commit.version_number.desc()).first()
    version_number = last_commit.version_number + 1 if last_commit else 1
    
    commit = Commit(
        repo_id=repo_id,
        user_id=current_user.id,
        message=message,
        commit_hash=commit_hash,
        version_number=version_number
    )
    
    db.session.add(commit)
    db.session.commit()
    
    return commit