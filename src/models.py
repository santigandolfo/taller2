import datetime
import os
from app import db, bcrypt, application, TOKEN_DURATION
import python_jwt as jwt
import json
from src.exceptions import BlacklistedTokenException, SignatureException, ExpiredTokenException, InvalidTokenException

BCRYPT_ROUNDS = int(os.environ["BCRYPT_ROUNDS"])
SECRET_KEY = os.environ.get("SECRET_KEY","key")


class User(object):
    """Generical User representation """

    username = ''
    ss_token = ''
    uid = ''

    def __init__(self, username, ss_token, uid):
        self.username = username
        self.ss_token = ss_token
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
            g = jwt.generate_jwt(payload,SECRET_KEY,algorithm='HS256',lifetime=datetime.timedelta(days=0, seconds=TOKEN_DURATION))
            application.logger.info(isinstance(g,unicode))
            return g
        except Exception as e: #pragma: no cover
            return e

    def update_ss_token(self,new_sstoken):
        """
        Updates the token used for operations with this user in the shared server
        """
        db.users.update_one({'uid':self.uid},{'$set':{'ss_token':new_sstoken}})
    def remove_from_db(self):
        """
        Removes itself from the db
        """
        db.users.delete_one({'uid':self.uid})

    @staticmethod
    def get_user_by_username(username):
        user_dict = db.users.find_one({'username':username})
        if not user_dict:
            return None
        return User(username=user_dict['username'],ss_token=user_dict['ss_token'],uid=user_dict['uid'])
    @staticmethod
    def get_user_by_uid(uid):
        user_dict = db.users.find_one({'uid':uid})
        if not user_dict:
            return None
        return User(username=user_dict['username'],ss_token=user_dict['ss_token'],uid=user_dict['uid'])

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            header, payload = jwt.verify_jwt(auth_token, SECRET_KEY,allowed_algs=['HS256'])
        except jwt.jws.exceptions.SignatureError as exc:
            raise SignatureException(auth_token)
        except Exception as exc:
            if (exc.message == 'expired'):
                raise ExpiredTokenException(auth_token)
            raise InvalidTokenException(auth_token)
        if (BlacklistToken.is_blacklisted(auth_token)):
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
        return db.blacklistedTokens.count({'token': token}) > 0
        

