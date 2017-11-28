from flask_testing import TestCase
from app import application, db


class BaseTestCase(TestCase):
    """ Base Tests """

    def create_app(self):
        return application

    def setUp(self):
        try:
            db.drivers.drop()
        except Exception:
            pass
        db.create_collection('drivers')
        try:
            db.riders.drop()
        except Exception:
            pass
        db.create_collection('riders')
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
        try:
            db.positions.drop()
        except Exception:
            pass
        db.create_collection('positions')
        try:
            db.trips.drop()
        except Exception:
            pass
        db.create_collection('trips')

    def tearDown(self):
        db.drop_collection('users')
        db.drop_collection('blacklistedTokens')
        db.drop_collection('drivers')
        db.drop_collection('riders')
        db.drop_collection('positions')
        db.drop_collection('trips')
