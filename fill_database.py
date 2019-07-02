from models import *
from lib import update

theme = Theme(name='Операции вывода')
update(theme)

school = School(name='Лицей при УлГТУ')
update(school)

userclass = Class(name='1-18', school=school)
update(school)

user = User(login='egor-sbrodov', password='123', name='Егор', surname='Сбродов', role=4, school=school, userclass=userclass)
update(user)

task1 = Task(name='Сумма чисел', body='Выведите сумму чисел', published=0, difficulty=2, author=user, theme=theme)
update(task1)

task2 = Task(name='Умножение', body='Выведите произведение чисел', published=1, difficulty=0, author=user, theme=theme)
update(task2)
