from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import Redis
import rq

app = Flask(__name__)
app.secret_key = 'AJSFGKUatsftakusftkt7t43qi'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/infolesson'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
queue = rq.Queue('infolesson-tasks', connection=Redis.from_url('redis://'))
db = SQLAlchemy(app, session_options={"expire_on_commit": False})
# db.session.expire_on_commit = False
