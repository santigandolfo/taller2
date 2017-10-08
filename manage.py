# manage.py


import os
import unittest
import coverage
from app import application
from flask_script import Manager


COV = coverage.coverage(
    branch=True,
    include='src/*',
    omit=[
        'tests/*',
    ]
)
COV.start()

manager = Manager(application)


@manager.command
def test():
    """Runs the unit tests without test coverage."""
    tests = unittest.TestLoader().discover('tests', pattern='test*.py')
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
