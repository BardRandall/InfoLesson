from flask import Blueprint
from lib import *

staff_module = Blueprint('staff', __name__, template_folder='templates')


@staff_module.route('/school/<int:school_id>/staff')
def school_staff(school_id):
    return delevop()
