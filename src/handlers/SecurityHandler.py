"""Handlers related with loging in and out an user"""

from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView

from app import db, application
from src.exceptions import ExpiredTokenException, InvalidTokenException
from src.models import User, BlacklistToken
from src.services.shared_server import validate_user
from src.mixins.AuthenticationMixin import Authenticator

SECURITY_BLUEPRINT = Blueprint('security', __name__)


class SecurityAPI(MethodView):
    """Handler for login/logout related API"""

    # LOGIN
    @staticmethod
    def post():
        """Endpoint for loging in a user, returns authentication token"""

        try:
            data = request.get_json()
            username = data.get('username')
            if not username:
                response = {
                    'status': 'fail',
                    'message': 'missing_username'
                }
                return make_response(jsonify(response)), 400
            application.logger.info("Login: {}".format(username))
            password = data.get('password')
            if not password:
                response = {
                    'status': 'fail',
                    'message': 'missing_password'
                }
                return make_response(jsonify(response)), 400
            application.logger.debug(type(username))
            user = User.get_user_by_username(username)
            if not user:
                response = {
                    'status': 'fail',
                    'message': 'unregistered_user'
                }
                return make_response(jsonify(response)), 409
            application.logger.info("Login: user exists")
            resp = validate_user(username, password)
            if resp.ok:
                user = User.get_user_by_username(username)
                application.logger.info("Login: password OK")
                auth_token = user.encode_auth_token()
                application.logger.info(isinstance(auth_token, unicode))
                response = {
                    'status': 'success',
                    'message': 'login_succesful',
                    'auth_token': auth_token
                }
                application.logger.debug('Generated json correctly')
                return make_response(jsonify(response)), 200
            else:
                response = {
                    'status': 'fail',
                    'message': 'wrong_password'
                }
                return make_response(jsonify(response)), 401

        except Exception as exc:  # pragma: no cover
            application.logger.error("Error ocurred. Message: " + exc.message +
                                     ".Doc: " + exc.__doc__)
            response = {
                'status': 'fail',
                'message': 'internal_error',
                'error_de': exc.message
            }
            return make_response(jsonify(response)), 500

    # LOGOUT
    @staticmethod
    def delete():
        """Endpoint for loging out a user, blacklists authentication token"""

        try:
            auth_header = request.headers.get('Authorization')
            token_username, error_message = Authenticator.authenticate(auth_header)
            if error_message:
                response = {
                    'status': 'fail',
                    'message': error_message
                }
                return make_response(jsonify(response)), 401
            auth_token = auth_header.split(" ")[1]
            application.logger.debug("Log Out: {}".format(auth_token))
            application.logger.info("Log Out: {}".format(token_username))
            blacklist_token = BlacklistToken(token=auth_token)
            application.logger.debug("blacklistToken created")
            db.blacklistedTokens.insert_one(blacklist_token.__dict__)
            application.logger.debug("blacklistToken inserted")
            response_object = {
                'status': 'success',
                'message': 'logout_succesful'
            }
            return make_response(jsonify(response_object)), 200
        except Exception as exc:  # pragma: no cover
            application.logger.error('Error msg: {0}. Error doc: {1}'
                                     .format(exc.message, exc.__doc__))
            response = {
                'status': 'fail',
                'message': 'internal_error'
            }
            return make_response(jsonify(response)), 500


# define the API resources
SECURITY_VIEW = SecurityAPI.as_view('security_api')

# add Rules for API Endpoints
SECURITY_BLUEPRINT.add_url_rule(
    '/security',
    view_func=SECURITY_VIEW,
    methods=['POST', 'DELETE']
)
