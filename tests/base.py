# project/server/tests/base.py


from flask_testing import TestCase

from app import application, db

class BaseTestCase(TestCase):
    """ Base Tests """

    def create_app(self):
        return application

    def setUp(self):
        try:
            db.users.drop()
        except Exception:
            pass
        db.create_collection('users')

    def tearDown(self):
        db.drop_collection('users')