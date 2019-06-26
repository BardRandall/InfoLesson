from flask import Blueprint
from lib import *
from models import *


class_module = Blueprint('classes', __name__, template_folder='templates')


@class_module.route('/classes')
def classes_list():
    if not check_access():
        return go_away()
    user = get_current_user()
    if user.role <= 1:
        return redirect(url_for('classes.class_info', class_id=user))
    classes = Class.query.filter_by(school=user.school).all()
    return render('classes-list.html', classes=classes)


@class_module.route('/class/<int:class_id>')
def class_info(class_id):
    return raise_error('Пока не доступно')


@class_module.route('/class/create')
def create():
    return raise_error('Пока не доступно')
