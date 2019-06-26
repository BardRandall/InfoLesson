import subprocess
import os
from lib import update
import time


# 0 - Waiting, 1 - Checking, 2 - Accepted, 3 - Wrong answer,
# 4 - Time Limit, 5 - Runtime Error, 6 - Server Error

WAITING = 0
CHECKING = 1
ACCEPTED = 2
WRONG_ANSWER = 3
TIME_LIMIT = 4
RUNTIME_ERROR = 5
SERVER_ERROR = 6


python_compiler = '/usr/bin/python'
c_compiler = '/usr/bin/python'
pascal_compiler = '/usr/bin/python'


def check_test(compiler, test, answer, time_limit, solution_path):
    try:
        process = subprocess.Popen([compiler, solution_path],
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(input=test.encode('utf-8') if test is not None else None, timeout=time_limit)
        stdout, stderr = stdout.decode('utf-8').rstrip(), stderr.decode('utf-8').rstrip()
        if stderr:
            return RUNTIME_ERROR, stderr
        else:
            if stdout == answer:
                return ACCEPTED, ''
            else:
                return WRONG_ANSWER, stdout
    except subprocess.TimeoutExpired:
        return TIME_LIMIT, ''
    except Exception as e:
        return SERVER_ERROR, str(e)


def check_attempt(attempt):
    attempt.status = CHECKING
    update(attempt)
    time.sleep(10)
    test_number = 1
    tests_folder = os.path.abspath('tests/' + str(attempt.task.id)) + '/'
    solution_path = os.path.abspath('solutions/{}.code'.format(attempt.id))  # TODO CHANGE EXTENSION and check existence
    logs = []
    while os.path.exists(tests_folder + '{}.in'.format(test_number)):
        with open(tests_folder + '{}.in'.format(test_number)) as f:
            test = f.read().rstrip()
        test = '\n'.join(['"' + x + '"' for x in test.splitlines()])
        with open(tests_folder + '{}.out'.format(test_number)) as f:
            answer = f.read().rstrip()
        compiler = python_compiler
        if attempt.language == 0:
            compiler = c_compiler
        elif attempt.language == 2:
            compiler = pascal_compiler
        verdict, info = check_test(compiler, test, answer, attempt.task.time_limit, solution_path)
        if verdict == ACCEPTED:
            logs.append('Test #{} - Accepted'.format(test_number))
            test_number += 1
            continue
        if verdict == WRONG_ANSWER:
            logs.append('Test #{} - Wrong answer'.format(test_number))
            logs.append('Test was: {}'.format(test))
            logs.append('Correct answer: {}'.format(answer))
            logs.append('Your answer: {}'.format(info))
        if verdict == TIME_LIMIT:
            logs.append('Test #{} - Time limit'.format(test_number))
        if verdict == RUNTIME_ERROR:
            logs.append('Test #{} - Runtime Error'.format(test_number))
            logs.append('Test was: {}'.format(test))
            logs.append('Stderr: \n{}'.format(info))
        if verdict == SERVER_ERROR:
            logs.append('Test #{} - Server Error'.format(test_number))
            logs.append('Test was: {}'.format(test))
            logs.append('Info: \n{}'.format(info))
        attempt.logs = '\n'.join(logs)
        attempt.status = verdict
        update(attempt)
        os.remove(solution_path)
        return
    attempt.logs = '\n'.join(logs)
    attempt.status = ACCEPTED
    update(attempt)
    os.remove(solution_path)
