from flask import Blueprint
from lib import *
from models import *


class_module = Blueprint('classes', __name__, template_folder='templates')


@class_module.route('/school/<int:school_id>')
def school_info(school_id):
    if not check_permission('school.profile.all'):
        return no_access()
    school = School.query.filter_by(id=school_id).first()
    if school is None:
        return not_exists('Школа', school_id)
    return render('school-info.html', school=school)


@class_module.route('/school/<int:school_id>/classes')
def classes_list(school_id):
    user = get_current_user()
    if not check_permission('school.classes-list', user=user):
        if user.userclass is not None:
            return redirect(url_for('classes.class_info', class_id=user.userclass.id))
        return raise_error('Вы не привязаны ни к какому классу')
    school = School.query.filter_by(id=school_id).first()
    if school is None:
        return not_exists('Школа', school_id)
    return render('classes-list.html', school=school)


@class_module.route('/class/<int:class_id>')
def class_info(class_id):
    user = get_current_user()
    userclass = Class.query.filter_by(id=class_id).first()
    if userclass is None:
        return not_exists('Класс', class_id)
    if user.userclass is None:
        if not(
                (check_permission('class.info.school', user=user) and user.school == userclass.school)
                or check_permission('class.info.all', user=user)
        ):
            return no_access()
    else:
        if not(
                (check_permission('class.info.self', user=user) and user.userclass.id == class_id)
                or (check_permission('class.info.school', user=user) and user.school == userclass.school)
                or check_permission('class.info.all', user=user)
        ):
            return no_access()
    return render('class-info.html', userclass=userclass)


@class_module.route('/school/<int:school_id>/class/create', methods=['GET', 'POST'])
def create(school_id):
    user = get_current_user()
    school = School.query.filter_by(id=school_id).first()
    if school is None:
        return not_exists('Школа', school_id)
    if not (
            (check_permission('class.create.school', user=user) and user.school == school)
            or check_permission('class.create.all', user=user)
    ):
        return no_access()
    if request.method == 'GET':
        return render('add-class.html', school=school)
    classname = request.form['classname']
    userclass = Class(name=classname, school=school)
    update(userclass)
    return redirect(url_for('classes.classes_list', school_id=school_id))


@class_module.route('/class/delete/<int:class_id>')
def delete(class_id):
    user = get_current_user()
    userclass = Class.query.filter_by(id=class_id).first()
    if userclass is None:
        return not_exists('Класс', class_id)
    if not(
            (check_permission('class.delete.school', user=user) and user.school == userclass.school)
            or check_permission('class.delete.all', user=user)
    ):
        return no_access()
    school_id = userclass.school.id
    remove(userclass)
    return redirect(url_for('classes.classes_list', school_id=school_id))


@class_module.route('/class/<int:class_id>/add', methods=['GET', 'POST'])
def add_student(class_id):
    userclass = Class.query.filter_by(id=class_id).first()
    if userclass is None:
        return not_exists('Класс', class_id)
    user = get_current_user()
    if not(
            (check_permission('class.add-student.school', user=user) and user.school == userclass.school)
            or check_permission('class.add-student.all', user=user)
    ):
        no_access()
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
