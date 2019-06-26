from flask import session, render_template, redirect, url_for, request
from models import User
from app import db
import random


def get_current_user():
    if 'login' not in session or 'password' not in session:
        return None
    return User.query.filter_by(login=session['login'], password=session['password']).first()


def get_hash(data):
    return data


def render(template, **kwargs):
    if 'current_user' in kwargs:
        current_user = kwargs['current_user']
    else:
        current_user = get_current_user()
    return render_template(template, current_user=current_user, **kwargs)


def raise_error(error='Неизвестная ошибка'):
    return render('errorpage.html', error=error)


def update(obj):
    db.session.add(obj)
    db.session.commit()
    db.session.expire_on_commit = False


def go_redirect():
    if 'redir' in request.args:
        return redirect(request.args['redir'])
    return go_away()


def go_away():
    return redirect(url_for('index'))


def generate_password(length=8):
    letters = 'qwertyuiopasdfghjklzxcvbnm1234567890QWERTYUIOPASDFGHJKLZXCVBNM'
    result = ''
    for i in range(length):
        result += random.choice(letters)
    return result


def check_access(level_access=1, higher=True):
    user = get_current_user()
    if user is None and level_access == 0:
        return True
    if user is None:
        return False
    return user.role >= level_access and higher or user.role <= level_access and not higher
