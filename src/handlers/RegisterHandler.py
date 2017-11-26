"""Handlers related with user registration"""

from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView

from app import db, application
from src.models import User
from src.services.shared_server import register_user, remove_user, update_user_data, get_data
from src.mixins.AuthenticationMixin import Authenticator

REGISTRATION_BLUEPRINT = Blueprint('users', __name__)


class RegisterAPI(MethodView):
    """Handler for registration related API"""

    @staticmethod
    def post():
        """Endpoint for signing up"""

        try:
            data = request.get_json()
            username = data.get('username')
            if not username:
                response = {
                    'status': 'fail',
                    'message': 'invalid_username'
                }
                return make_response(jsonify(response)), 400
            application.logger.info("Registration: {}".format(username))
            password = data.get('password')
            if not password:
                response = {
                    'status': 'fail',
                    'message': 'missing_password'
                }
                return make_response(jsonify(response)), 400
            application.logger.debug(type(username))
            search_pattern = {'username': username}
            if db.users.count(search_pattern) > 0:
                response = {
                    'status': 'fail',
                    'message': 'user_username_already_exists'
                }
                return make_response(jsonify(response)), 409
            resp = register_user(data)
            if resp.ok:
                application.logger.info('User registered')
                user = User(username=username, uid=resp.json()['id'])
                db.users.insert_one(user.__dict__)
                user_type = data['type']
                if user_type == "driver":
                    db.drivers.insert_one({'username': username, 'available': False})
                else:
                    db.riders.insert_one({'username': username})
                auth_token = user.encode_auth_token()
                application.logger.debug(isinstance(auth_token, unicode))
                response = {
                    'status': 'success',
                    'message': 'user_registered',
                    'auth_token': auth_token,
                    'id': resp.json().get('id')
                }
                application.logger.debug('Generated json correctly')
                return make_response(jsonify(response)), 201
            else:
                return make_response(jsonify(resp.json())), resp.status_code
        except Exception as exc:
            application.logger.error("Error ocurred. Message: {} .Doc: {}"
                                     .format(exc.message, exc.__doc__))
            response = {
                'status': 'fail',
                'message': 'internal_error',
                'error_description': exc.message
            }
            return make_response(jsonify(response)), 500

    @staticmethod
    def delete(username):
        """Endpoint for erasign an user"""

        try:
            application.logger.info("Asked to remove user: {}".format(username))
            user = User.get_user_by_username(username)
            if not user:
                response = {
                    'status': 'fail',
                    'message': 'user_not_found'
                }
                return make_response(jsonify(response)), 404
            application.logger.info("user {} exists".format(username))
            auth_header = request.headers.get('Authorization')
            token_username, error_message = Authenticator.authenticate(auth_header)
            if error_message:
                response = {
                    'status': 'fail',
                    'message': error_message
                }
                return make_response(jsonify(response)), 401
            application.logger.info("Removing user w/ Auth: {}".format(auth_header))
            application.logger.info("Deletion was requested by: {}".format(token_username))
            if token_username == username:
                application.logger.info("Permission granted")
                application.logger.info("User to remove {}".format(token_username))
                application.logger.debug(type(token_username))
                resp = remove_user(user.uid)
                if resp.ok:
                    response = {
                        'status': 'success',
                        'message': 'user_deleted'
                    }
                    user.remove_from_db()
                    return make_response(jsonify(response)), 203
                else:
                    return make_response(jsonify(resp.json())), resp.status_code
            else:
                response = {
                    'status': 'fail',
                    'message': 'unauthorized_deletion'
                }
                return make_response(jsonify(response)), 401
        except Exception as exc:  # pragma: no cover

            application.logger.error('Error msg: {0}. Error doc: {1}'
                                     .format(exc.message, exc.__doc__))
            response = {
                'status': 'fail',
                'message': 'internal_error',
                'error_description': exc.message
            }
            return make_response(jsonify(response)), 500

    @staticmethod
    def put(username):
        """Endpoint for modifying an user's general info"""

        try:
            application.logger.info("Asked to update user: {}".format(username))
            user = User.get_user_by_username(username)
            if not user:
                response = {
                    'status': 'fail',
                    'message': 'user_not_found'
                }
                return make_response(jsonify(response)), 404
            application.logger.info("user {} exists".format(username))
            auth_header = request.headers.get('Authorization')
            token_username, error_message = Authenticator.authenticate(auth_header)
            if error_message:
                response = {
                    'status': 'fail',
                    'message': error_message
                }
                return make_response(jsonify(response)), 401
            application.logger.info("Updating user w/ Auth: {}".format(auth_header))
            application.logger.info("Update was requested by: {}".format(token_username))
            if token_username == username:
                application.logger.info("Permission granted")
                application.logger.info("User to update {}".format(token_username))
                application.logger.debug(type(token_username))
                data = request.get_json()
                resp = update_user_data(user.uid, data)
                if resp.ok:
                    response = {
                        'status': 'success',
                        'message': 'data_changed_succesfully'
                    }
                    return make_response(jsonify(response)), 200
                else:
                    return make_response(jsonify(resp.json())), resp.status_code
            else:
                response = {
                    'status': 'fail',
                    'message': 'unauthorized_update'
                }
                return make_response(jsonify(response)), 401
        except Exception as exc:  # pragma: no cover
            application.logger.error('Error msg: {0}. Error doc: {1}'
                                     .format(exc.message, exc.__doc__))
            response = {
                'status': 'fail',
                'message': 'internal_error',
                'error_description': exc.message
            }
            return make_response(jsonify(response)), 500

    @staticmethod
    def get(username):
        """Get a user info"""
        try:
            user = User.get_user_by_username(username)
            if not user:
                response = {
                    'status': 'fail',
                    'message': 'user_not_found'
                }
                return make_response(jsonify(response)), 404
            resp = get_data(user.uid)
            if resp.ok:
                response = {
                    'status': 'success',
                    'message': 'data_retrieved',
                    'info': resp.json()
                }
                return make_response(jsonify(response)), 200
            else:
                return make_response(jsonify(resp.json())), resp.status_code
        except Exception as exc:  # pragma: no cover
            application.logger.error('Error msg: {0}. Error doc: {1}'
                                     .format(exc.message, exc.__doc__))
            response = {
                'status': 'fail',
                'message': 'internal_error',
                'error_description': exc.message
            }
            return make_response(jsonify(response)), 500


# define the API resources
REGISTRATION_VIEW = RegisterAPI.as_view('registration_api')

# add Rules for API Endpoints
REGISTRATION_BLUEPRINT.add_url_rule(
    '/users',
    view_func=REGISTRATION_VIEW,
    methods=['POST']
)

REGISTRATION_BLUEPRINT.add_url_rule(
    '/users/<username>',
    view_func=REGISTRATION_VIEW,
    methods=['DELETE', 'PUT', 'GET']
)
