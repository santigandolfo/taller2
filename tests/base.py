# project/server/tests/base.py


from flask_testing import TestCase

from app import application, db

class BaseTestCase(TestCase):
    """ Base Tests """

    def create_app(self):
        return application

    def setUp(self):
        try:
            db.activedrivers.drop()
        except Exception:
            pass
        db.create_collection('activedrivers')
        try:
            db.users.drop()
        except Exception:
            pass
        db.create_collection('users')
        try:
            db.blacklistedTokens.drop()
        except Exception:
            pass
        db.create_collection('blacklistedTokens')

    def tearDown(self):
        db.drop_collection('users')
        db.drop_collection('blacklistedTokens')
        db.drop_collection('activedrivers')
        