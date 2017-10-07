import datetime
import os
from app import db, bcrypt, application
import python_jwt as jwt
import json

BCRYPT_ROUNDS = int(os.environ["BCRYPT_ROUNDS"])
SECRET_KEY = os.environ.get("SECRET_KEY","key")
SALT_LENGTH = 16


class User(object):
    """Generical User representation """

    email = ''
    password = ''
    salt = ''

    def __init__(self, email, password):
        self.email = email
        self.salt = unicode(os.urandom(SALT_LENGTH),errors='replace')
        self.password = bcrypt.generate_password_hash(
            password+self.salt, BCRYPT_ROUNDS
        )
        
    def check_pw(self, password):
        return bcrypt.check_password_hash(
                self.password, password+self.salt)
            


    def encode_auth_token(self):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=5),
                'iat': datetime.datetime.utcnow(),
                'sub': self.email
            }
            return jwt.generate_jwt(
                payload,
                SECRET_KEY,
                algorithm='HS256'
            )
        except Exception as e:
            return e


    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, SECRET_KEY)
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'


class BlacklistToken(object):
    """
    Token Model for storing invalid JWT
    """

    
    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    def __repr__(self):
        return '<id: token: {}'.format(self.token)

