import datetime
import os
from app import db, bcrypt, application, TOKEN_DURATION
import python_jwt as jwt
import json

BCRYPT_ROUNDS = int(os.environ["BCRYPT_ROUNDS"])
SECRET_KEY = os.environ.get("SECRET_KEY","key")


class User(object):
    """Generical User representation """

    email = ''
    password = ''

    def __init__(self, email, password):
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password, BCRYPT_ROUNDS
        )

    def encode_auth_token(self):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'sub': self.email
            }
            g = jwt.generate_jwt(payload,SECRET_KEY,algorithm='HS256',lifetime=datetime.timedelta(days=0, seconds=TOKEN_DURATION))
            application.logger.info(isinstance(g,unicode))
            return g
        except Exception as e:
            return e


    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        header,payload = jwt.verify_jwt(auth_token, SECRET_KEY,allowed_algs=['HS256'])
        application.logger.debug('Verified token .Info: {}'.format(payload['sub']))
        return payload['sub']


class BlacklistToken(object):
    """
    Token Model for storing invalid JWT
    """


    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    def __repr__(self):
        return '<id: token: {}'.format(self.token)
