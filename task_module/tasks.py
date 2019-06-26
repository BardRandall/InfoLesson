from flask import Blueprint

import os
import math

from app import queue
from lib import *
from models import *

task_module = Blueprint('tasks', __name__, template_folder='templates')


@task_module.route('/collection')  # TODO добавить статистику, сколько человек решило задачу, сколько процентов и т. д.
def collection():  # TODO переделать
    if not check_access(2):
        return raise_error('У вас нет доступа к этой странице')
    if request.args.get('search') is not None:
        if check_access(4):
            tasks = Task.query.filter(Task.name.like('%' + request.args['search'] + '%')).all()
        else:
            tasks1 = Task.query.filter(Task.name.like('%' + request.args['search'] + '%'), Task.published == 1).all()
            tasks2 = Task.query.filter(Task.name.like('%' + request.args['search'] + '%'), Task.published == 0, Task.author == get_current_user()).all()
            tasks = tasks1 + tasks2
    elif 'id' in request.args or 'theme' in request.args or 'level' in request.args:
        params = {}
        if request.args.get('id'):
            params['id'] = int(request.args['id'])
        if request.args.get('theme') and request.args.get('theme') != '-1':
            params['theme'] = Theme.query.filter_by(id=int(request.args['theme'])).first()
        if request.args.get('level') and request.args.get('level') != '-1':
            params['difficulty'] = int(request.args['level'])
        if check_access(4):
            tasks = Task.query.filter_by(**params).all()
        else:
            tasks1 = Task.query.filter_by(**params, published=1).all()
            tasks2 = Task.query.filter_by(**params, published=0, user=get_current_user()).all()
            tasks = tasks1 + tasks2
    else:
        if check_access(4):
            tasks = Task.query.all()
        else:
            tasks1 = Task.query.filter_by(published=1).all()
            tasks2 = Task.query.filter_by(published=0, author=get_current_user()).all()
            tasks = tasks1 + tasks2
    themes = Theme.query.all()
    count_on_page = 10
    pages = math.ceil(len(tasks) / count_on_page)
    if 'page' in request.args:
        if request.args['page'] > str(count_on_page):
            return raise_error('Страницы с таким номером не существует')
        page = int(request.args['page'])
        tasks = tasks[count_on_page * (page - 1):count_on_page * page]
    else:
        tasks = tasks[:count_on_page]
    return render('collection.html', tasks=tasks, themes=themes, pages=pages)


@task_module.route('/task/create', methods=['GET', 'POST'])
def create_task():
    if not check_access(2):
        return raise_error('У вас нет доступа к этому разделу')
    return render('create-task.html')


@task_module.route('/task/<int:task_id>', methods=['GET', 'POST'])
def task(task_id):
    if not check_access():
        return go_away()
    current_task = Task.query.filter_by(id=task_id).first()
    current_user = get_current_user()
    if current_task is None:
        return raise_error('Задание с id {} не существует'.format(task_id))
    if request.method == 'POST':
        file = request.files['solution']
        language = int(request.form['language'])
        code = file.read()
        attempt = Attempt(task=current_task, language=language, sender=current_user, code=code)
        update(attempt)
        job = queue.enqueue('checker.check_attempt', attempt)
        attempt.queue_id = job.get_id()
        update(attempt)
        with open('solutions/{}.code'.format(attempt.id), mode='w+', encoding='utf8') as f:
            f.write(('#!/usr/bin/env python\n# -*- coding: utf-8 -*-\n' if language == 1 else '') + code.decode('utf8'))
        file.close()
    examples_of_tests = []
    for i in range(1, current_task.examples_of_tests + 1):
        if not os.path.exists('tests/{}/{}.in'.format(current_task.id, i)):
            break
        with open('tests/{}/{}.in'.format(current_task.id, i)) as f:
            examples_of_tests.append([f.read()])
        with open('tests/{}/{}.out'.format(current_task.id, i)) as f:
            examples_of_tests[i - 1].append(f.read())
    if request.args.get('all') is None or check_access(1, higher=False):
        return render('task.html', task=current_task,
                      attempts=Attempt.query.filter_by(sender=current_user, task=current_task).order_by(Attempt.time_created.desc()).all(),
                      examples_of_tests=examples_of_tests)
    return render('task.html', task=current_task,
                  attempts=Attempt.query.filter_by(task=current_task).order_by(Attempt.time_created.desc()).all(),
                  all=True,
                  examples_of_tests=examples_of_tests)


@task_module.route('/attempt/<int:attempt_id>')
def attempt(attempt_id):
    attempt = Attempt.query.filter_by(id=attempt_id).first()
    if attempt is None:
        return raise_error('Такой попытки не существует')
    if not (check_access(2) or attempt.sender == get_current_user()):
        return raise_error('У вас нет доступа к этой попытке')
    return render('attempt.html', attempt=attempt)


@task_module.route('/attempt/delete/<int:attempt_id>')
def delete_attempt(attempt_id):
    attempt = Attempt.query.filter_by(id=attempt_id).first()
    if attempt is None:
        return raise_error('Такой попытки не существует')
    if not check_access(4):
        return raise_error('У вас нет доступа к этому действию')
    db.session.delete(attempt)
    db.session.commit()
    return go_redirect()


@task_module.route('/attempt/edit/<int:attempt_id>', methods=['GET', 'POST'])
def edit_attempt(attempt_id):
    attempt = Attempt.query.filter_by(id=attempt_id).first()
    if attempt is None:
        return raise_error('Такой попытки не существует')
    if not check_access(4):
        return raise_error('У вас нет доступа к этому действию')
    if request.method == 'GET':
        return render('edit-attempt.html', current_status=attempt.status)
    status = int(request.form['status'])
    attempt.status = status
    update(attempt)
    return go_redirect()
