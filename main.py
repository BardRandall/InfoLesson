from app import app
from lib import render
from auth_module.auth import auth_module
from task_module.tasks import task_module
from class_module.classes import class_module


app.register_blueprint(auth_module)
app.register_blueprint(task_module)
app.register_blueprint(class_module)


@app.route('/')
def index():
    return render('index.html')


app.run(host='127.0.0.1', port=8080, debug=True)
