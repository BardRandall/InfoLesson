from flask import Blueprint
from lib import *
from models import *


class_module = Blueprint('classes', __name__, template_folder='templates')


@class_module.route('/school/<int:school_id>')
def school_info(school_id):
    if not check_access():
        return go_away()
    school = School.query.filter_by(id=school_id).first()
    if school is None:
        return raise_error('Школа с id {} не существует'.format(school_id))
    return render('school-info.html', school=school)


@class_module.route('/school/<int:school_id>/classes')
def classes_list(school_id):
    user = get_current_user()
    if user.role == 0:
        return go_away()
    if user.role == 1:
        if user.userclass is not None:
            return redirect(url_for('classes.class_info', class_id=user.userclass.id))
        return go_away()
    school = School.query.filter_by(id=school_id).first()
    if school is None:
        return raise_error('Школы с id {} не существует'.format(school_id))
    return render('classes-list.html', school=school)


@class_module.route('/class/<int:class_id>')
def class_info(class_id):
    user = get_current_user()
    if user.role == 0:
        return go_away()
    userclass = Class.query.filter_by(id=class_id).first()
    if userclass is None:
        return raise_error('Класс с id {} не существует'.format(class_id))
    if user.role == 1 and user.userclass != userclass:
        return raise_error('Вы находитесь в другом классе')
    if user.role == 2 and user.school != userclass.school:
        return raise_error('Этот класс не принадлежит вашей школе')
    return render('class-info.html', userclass=userclass)


@class_module.route('/school/<int:school_id>/class/create')
def create(school_id):
    return raise_error('Пока не доступно')


@class_module.route('/class/delete/<int:class_id>')
def delete(class_id):
    return raise_error('Пока не доступно')


@class_module.route('/class/<int:class_id>/add', methods=['GET', 'POST'])
def add_student(class_id):
    if not check_access(2):
        return go_away()
    userclass = Class.query.filter_by(id=class_id).first()
    if userclass is None:
        return raise_error('Класс с id {} не существует'.format(class_id))
    user = get_current_user()
    if not (user.school == userclass.school or user.role >= 4):
        return raise_error('У вас нет доступа к этому действию')
    if request.method == 'GET':
        return render('add-student.html', userclass=userclass)
    else:
        username = request.form['username']
        usersurname = request.form['usersurname']
        userlogin = request.form['userlogin']
        if not (username and usersurname):
            return render('add-student.html', userclass=userclass, empty=True,
                          username=username, usersurname=usersurname, userlogin=userlogin)
        auto = False
        if not userlogin:
            auto = True
            userlogin = generate_login(username, usersurname)
        if User.query.filter_by(login=userlogin).first() is not None:
            if auto:
                return render('add-student.html', userclass=userclass,
                              auto_compare=True, username=username, usersurname=usersurname, userlogin=userlogin)
            return render('add-student.html', userclass=userclass,
                          manual_compare=True, username=username, usersurname=usersurname, userlogin=userlogin)
        userpassword = generate_password()
        new_user = User(login=userlogin, password=get_hash(userpassword), name=username, surname=usersurname,
                        role=1, userclass=userclass, school=userclass.school)
        update(new_user)
        return render('success-add.html', new_user=new_user, password=userpassword)
