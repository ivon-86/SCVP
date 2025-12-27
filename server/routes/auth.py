from flask import Blueprint

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return "Страница входа в разработке"

@auth.route('/register')
def register():
    return "Страница регистрации в разработке"