# manage.py
import coverage

COV = coverage.coverage(
    branch=True,
    include='src/*',
    omit=[
        'tests/*',
    ]
)
COV.start()

import logging
import os
import unittest
from app import application
from flask_script import Manager

LOG_LEVEL = os.environ["LOG_LEVEL"]


manager = Manager(application)
logging.disable(LOG_LEVEL) #Salida mas limpia por pantalla


@manager.command
def test():
    """Runs the unit tests without test coverage."""
    tests = unittest.TestLoader().discover('tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1

@manager.command
def test_registration():
    """Runs the registration unit tests without test coverage."""
    tests = unittest.TestLoader().discover('tests', pattern='test_registration.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1

@manager.command
def test_security():
    """Runs the security unit tests without test coverage."""
    tests = unittest.TestLoader().discover('tests', pattern='test_security.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1

@manager.command
def test_requests():
    """Runs the requests unit tests without test coverage."""
    tests = unittest.TestLoader().discover('tests', pattern='test_requests.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1

@manager.command
def test_trips():
    """Runs the trips unit tests without test coverage."""
    tests = unittest.TestLoader().discover('tests', pattern='test_trips.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1

@manager.command
def test_user_manipulation():
    """Runs the user manipulation unit tests without test coverage."""
    tests = unittest.TestLoader().discover('tests', pattern='test_user_manipulation.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1

@manager.command
def test_driver_manipulation():
    """Runs the driver manipulation unit tests without test coverage."""
    tests = unittest.TestLoader().discover('tests', pattern='test_driver_manipulation.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1

@manager.command
def test_car_manipulation():
    """Runs the car manipulation unit tests without test coverage."""
    tests = unittest.TestLoader().discover('tests', pattern='test_car_manipulation.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1

@manager.command
def test_positions():
    """Runs the position unit tests without test coverage."""
    tests = unittest.TestLoader().discover('tests', pattern='test_positions.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1

@manager.command
def test_notifiactions_token():
    """Runs the notifications token tests without test coverage."""
    tests = unittest.TestLoader().discover('tests', pattern='test_push_notification_manipulation.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1

@manager.command
def test_request_matching():
    """Runs the matching without test coverage."""
    tests = unittest.TestLoader().discover('tests', pattern='test_request_matching.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1

@manager.command
def test_request_cancellation():
    """Runs the matching without test coverage."""
    tests = unittest.TestLoader().discover('tests', pattern='test_request_cancellation.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


@manager.command
def cov():
    """Runs the unit tests with coverage."""
    tests = unittest.TestLoader().discover('tests')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        return 0
    return 1


if __name__ == '__main__':
    manager.run()
