from flask import Blueprint, request, session, redirect, url_for
from lib import *
from models import User

auth_module = Blueprint('auth', __name__, template_folder='templates')


@auth_module.route('/login', methods=['GET', 'POST'])
def login():
    if check_access(level_access=1, higher=True):
        return go_away()
    if request.method == 'GET':
        return render('login.html')
    log = request.form['login']
    password = get_hash(request.form['password'])
    user = User.query.filter_by(login=log, password=password).first()
    if user is None:
        return render('login.html', error=True)
    session['login'] = log
    session['password'] = password
    return go_away()


@auth_module.route('/user/<int:user_id>')
def userpage(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return raise_error('Такого пользователя не существует')
    return render('userpage.html', user=user, new_password=request.args.get('new_password'))


@auth_module.route('/registration')
def register():
    if check_access(level_access=1, higher=True):
        return go_away()
    return render('register.html')


@auth_module.route('/logout')
def logout():
    session.pop('login', None)
    session.pop('password', None)
    return go_away()


@auth_module.route('/edit-role/<int:user_id>', methods=['GET', 'POST'])
def edit_role(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return raise_error('Такого пользователя не существует')
    if not check_access(4):
        return raise_error('У вас нет доступа к этому действию')
    if request.method == 'GET':
        return render('edit-role.html', current_role=user.role)
    user.role = int(request.form['role'])
    update(user)
    return go_redirect()


@auth_module.route('/reset-password/<int:user_id>')
def reset_password(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return raise_error('Такого пользователя не существует')
    if not check_access(4):
        return raise_error('У вас нет доступа к этому действию')
    new_pass = generate_password()
    user.password = get_hash(new_pass)
    update(user)
    return redirect(url_for('auth.userpage', user_id=user_id, new_password=new_pass))
