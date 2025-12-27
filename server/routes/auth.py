from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from server.forms import LoginForm, RegistrationForm
from server.models import User, db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа"""
    # Если пользователь уже авторизован, перенаправляем на dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        # Ищем пользователя в базе данных
        user = User.query.filter_by(username=form.username.data).first()
        
        # Проверяем пароль
        if user and user.check_password(form.password.data):
            # Авторизуем пользователя
            login_user(user, remember=form.remember.data)
            flash('Вы успешно вошли в систему!', 'success')
            
            # Перенаправляем на dashboard
            return redirect(url_for('main.dashboard'))
        else:
            flash('Неверное имя пользователя или пароль', 'error')
    
    return render_template('login.html', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Страница регистрации"""
    # Если пользователь уже авторизован, перенаправляем на dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # Создаём нового пользователя
        user = User(
            username=form.username.data,
            email=form.email.data if form.email.data else None
        )
        
        # Устанавливаем пароль
        user.set_password(form.password.data)
        
        # Сохраняем в базу данных
        try:
            db.session.add(user)
            db.session.commit()
            flash('Регистрация успешна! Теперь вы можете войти в систему.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Произошла ошибка при регистрации. Попробуйте ещё раз.', 'error')
    
    return render_template('register.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    """Выход из системы"""
    logout_user()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('main.index'))