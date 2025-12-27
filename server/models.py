from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from server import db

class User(UserMixin, db.Model):
    """Модель пользователя"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    theme = db.Column(db.String(10), default='light')
    
    # Связи
    repositories = db.relationship('Repository', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    commits = db.relationship('Commit', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Хеширование пароля"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Проверка пароля"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Repository(db.Model):
    """Модель репозитория"""
    __tablename__ = 'repositories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_public = db.Column(db.Boolean, default=False)
    
    # Связи
    commits = db.relationship('Commit', backref='repository', lazy='dynamic', cascade='all, delete-orphan')
    files = db.relationship('RepoFile', backref='repository', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Repository {self.name}>'

class Commit(db.Model):
    """Модель коммита (изменения)"""
    __tablename__ = 'commits'
    
    id = db.Column(db.Integer, primary_key=True)
    repo_id = db.Column(db.Integer, db.ForeignKey('repositories.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    commit_hash = db.Column(db.String(64), unique=True, nullable=False)
    parent_hash = db.Column(db.String(64), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    version_number = db.Column(db.Integer, nullable=False, default=1)
    
    def __repr__(self):
        return f'<Commit {self.commit_hash[:8]}: {self.message}>'

class RepoFile(db.Model):
    """Модель файла в репозитории"""
    __tablename__ = 'repo_files'
    
    id = db.Column(db.Integer, primary_key=True)
    repo_id = db.Column(db.Integer, db.ForeignKey('repositories.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)  # Относительный путь
    content_hash = db.Column(db.String(64), nullable=False)
    size = db.Column(db.Integer, nullable=False)  # Размер в байтах
    is_directory = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<RepoFile {self.filename}>'