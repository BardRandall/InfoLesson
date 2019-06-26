from flask import Blueprint
from lib import *


class_module = Blueprint('classes', __name__, template_folder='templates')


@class_module.route('/classes')
def classes():
    return raise_error('Данный функционал не доступен')
