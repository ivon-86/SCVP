from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, ValidationError
from server.models import User


class LoginForm(FlaskForm):
    """Форма входа"""
    username = StringField('Имя пользователя', 
                          validators=[DataRequired(), 
                                     Length(min=3, max=64)],
                          render_kw={"placeholder": "Введите имя пользователя"})
    
    password = PasswordField('Пароль', 
                            validators=[DataRequired(), 
                                       Length(min=6)],
                            render_kw={"placeholder": "Введите пароль"})
    
    remember = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    """Форма регистрации"""
    username = StringField('Имя пользователя', 
                          validators=[DataRequired(), 
                                     Length(min=3, max=64)],
                          render_kw={"placeholder": "Придумайте имя пользователя"})
    
    email = StringField('Email', 
                       validators=[Optional(), 
                                  Email(), 
                                  Length(max=120)],
                       render_kw={"placeholder": "email@example.com (необязательно)"})
    
    password = PasswordField('Пароль', 
                            validators=[DataRequired(), 
                                       Length(min=6)],
                            render_kw={"placeholder": "Не менее 6 символов"})
    
    confirm_password = PasswordField('Подтвердите пароль', 
                                    validators=[DataRequired(), 
                                               EqualTo('password', message='Пароли должны совпадать')],
                                    render_kw={"placeholder": "Повторите пароль"})
    
    submit = SubmitField('Зарегистрироваться')
    
    def validate_username(self, username):
        """Проверка уникальности имени пользователя"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Это имя пользователя уже занято. Выберите другое.')


class NewRepoForm(FlaskForm):
    """Форма создания нового репозитория"""
    name = StringField('Название репозитория', 
                      validators=[DataRequired(), 
                                 Length(min=3, max=100)],
                      render_kw={"placeholder": "my-awesome-project"})
    
    description = TextAreaField('Описание', 
                               validators=[Optional(), 
                                         Length(max=500)],
                               render_kw={"placeholder": "Краткое описание вашего проекта...",
                                        "rows": 4})
    
    generate_readme = BooleanField('Сгенерировать README.md файл', default=True)
    is_public = BooleanField('Сделать репозиторий публичным')
    submit = SubmitField('Создать репозиторий')


class EditRepoForm(FlaskForm):
    """Форма редактирования репозитория"""
    name = StringField('Название репозитория', 
                      validators=[DataRequired(), 
                                 Length(min=3, max=100)],
                      render_kw={"placeholder": "Название репозитория"})
    
    description = TextAreaField('Описание', 
                               validators=[Optional(), 
                                         Length(max=500)],
                               render_kw={"placeholder": "Описание репозитория...",
                                        "rows": 4})
    
    is_public = BooleanField('Сделать репозиторий публичным')
    submit = SubmitField('Сохранить изменения')


class UploadFileForm(FlaskForm):
    """Форма загрузки файла"""
    file = FileField('Файл', 
                    validators=[FileRequired(), 
                               FileAllowed(['txt', 'py', 'js', 'html', 'css', 'md', 'json', 'xml', 
                                           'jpg', 'png', 'gif', 'pdf', 'zip', 'tar', 'gz'], 
                                          'Недопустимый тип файла')])
    
    filepath = StringField('Путь (опционально)', 
                          validators=[Optional()],
                          render_kw={"placeholder": "folder/subfolder/"})
    
    submit = SubmitField('Загрузить файл')


class NewFolderForm(FlaskForm):
    """Форма создания новой папки"""
    folder_name = StringField('Имя папки', 
                             validators=[DataRequired(), 
                                        Length(min=1, max=100)],
                             render_kw={"placeholder": "Название папки"})
    
    folder_path = StringField('Путь (опционально)', 
                             validators=[Optional()],
                             render_kw={"placeholder": "folder/subfolder/"})
    
    submit = SubmitField('Создать папку')


class EditFileForm(FlaskForm):
    """Форма редактирования файла"""
    content = TextAreaField('Содержимое файла', 
                          validators=[DataRequired()],
                          render_kw={"rows": 20})
    
    filename = HiddenField()
    submit = SubmitField('Сохранить файл')