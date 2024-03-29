from app import db


class School(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))


class Theme(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    name = db.Column(db.String(50))
    surname = db.Column(db.String(50))
    role = db.Column(db.Integer, default=1)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'))
    school = db.relationship('School', backref=db.backref('persons', lazy=True))

    userclass_id = db.Column(db.Integer, db.ForeignKey('class.id'))
    userclass = db.relationship('Class', backref=db.backref('students', lazy=True))


class Task(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    body = db.Column(db.Text(2000))
    time_limit = db.Column(db.Integer, default=1)  # in seconds
    examples_of_tests = db.Column(db.Integer, default=1)
    published = db.Column(db.Integer, default=0)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    author = db.relationship('User', backref=db.backref('added_tasks', lazy=True))
    difficulty = db.Column(db.Integer, default=0)  # 0 - Базовая, 1 - Повышенный, 2 - Высокий, 3 - Олимпиадный
    theme_id = db.Column(db.Integer, db.ForeignKey('theme.id'))

    theme = db.relationship('Theme', backref=db.backref('tasks', lazy=True))


class Attempt(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    task = db.relationship('Task', backref=db.backref('attempts', lazy=True))
    language = db.Column(db.Integer, default=0)  # 0 - C++, 1 - Python, 2 - Pascal
    time_created = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sender = db.relationship('User')
    code = db.Column(db.Text(2000))
    logs = db.Column(db.Text(1000))
    queue_id = db.Column(db.String(100))
    status = db.Column(db.Integer, default=0)  # 0 - Waiting, 1 - Checking, 2 - Accepted, 3 - Wrong answer,
    # 4 - Time Limit, 5 - Runtime Error, 6 - Server Error


class Class(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'))
    school = db.relationship('School', backref=db.backref('classes', lazy=True))


db.create_all()
