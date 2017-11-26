"""Entitys saved in the db"""
import datetime
import os

import python_jwt as jwt

from app import db, application, TOKEN_DURATION
from src.exceptions import BlacklistedTokenException, SignatureException, ExpiredTokenException, \
    InvalidTokenException

SECRET_KEY = os.environ.get("SECRET_KEY", "key")


class User(object):
    """Generical User representation """

    username = ''
    uid = ''

    def __init__(self, username, uid):
        self.username = username
        self.uid = uid

    def encode_auth_token(self):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'sub': self.username
            }
            auth_token = jwt.generate_jwt(payload, SECRET_KEY, algorithm='HS256',
                                          lifetime=datetime
                                          .timedelta(days=0, seconds=TOKEN_DURATION))
            application.logger.info(isinstance(auth_token, unicode))
            return auth_token
        except Exception as exc:  # pragma: no cover
            return exc

    def remove_from_db(self):
        """
        Removes itself from the db
        """
        db.users.delete_one({'uid': self.uid})

    @staticmethod
    def get_user_by_username(username):
        """Given a username return the corresponding user"""
        user_dict = db.users.find_one({'username': username})
        if not user_dict:
            return None
        return User(username=user_dict['username'], uid=user_dict['uid'])

    @staticmethod
    def get_user_by_uid(uid):
        """Given a user_id return the corresponding user"""
        user_dict = db.users.find_one({'uid': uid})
        if not user_dict:
            return None
        return User(username=user_dict['username'], uid=user_dict['uid'])

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            _, payload = jwt.verify_jwt(auth_token, SECRET_KEY, allowed_algs=['HS256'])
        except jwt.jws.exceptions.SignatureError:
            raise SignatureException(auth_token)
        except Exception as exc:
            if exc.message == 'expired':
                raise ExpiredTokenException(auth_token)
            raise InvalidTokenException(auth_token)
        if BlacklistToken.is_blacklisted(auth_token):
            raise BlacklistedTokenException(auth_token)

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

    @staticmethod
    def is_blacklisted(token):
        """Returns true if a user has logged out using this token"""
        return db.blacklistedTokens.count({'token': token}) > 0
