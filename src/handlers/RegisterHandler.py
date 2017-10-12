import python_jwt as jwt
from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from app import db, application
from src.models import  User
from src.exceptions import BlacklistedTokenException, SignatureException, ExpiredTokenException, InvalidTokenException


registration_blueprint = Blueprint('users', __name__)

class RegisterAPI(MethodView):
    """Handler for registration related API"""

    def post(self):

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
            search_pattern = {'username' : username}
            if db.users.count(search_pattern) > 0:
                response = {
                    'status': 'fail',
                    'message': 'user_username_already_exists'
                }
                return make_response(jsonify(response)), 409

            application.logger.debug('User not found while registering.OK')
            user = User(username=username,password=password)
            application.logger.debug('User created')
            db.users.insert_one(user.__dict__)
            application.logger.debug('User inserted')
            auth_token = user.encode_auth_token()
            application.logger.info(isinstance(auth_token,unicode))
            response = {
                'status': 'success',
                'message': 'user_registered',
                'auth_token': auth_token
            }
            application.logger.debug('Generated json correctly')
            return make_response(jsonify(response)), 201
        except Exception as exc:
            application.logger.error("Error ocurred. Message: {} .Doc: {}".format(exc.message, exc.__doc__))
            response = {
                'status': 'fail',
                'message': 'internal_error',
                'error_de': exc.message
            }
            return make_response(jsonify(response)), 500 

    def delete(self):
        try:
            auth_header = request.headers.get('Authorization')
            if auth_header:
                auth_token = auth_header.split(" ")[1]
            else:
                auth_token = ''
            application.logger.info("Removing user. Auth: {}".format(auth_token))
            if auth_token:
                username_user = User.decode_auth_token(auth_token)
                application.logger.info("User to remove {}".format(username_user))
                application.logger.debug(type(username_user))
                if isinstance(username_user, str) or isinstance(username_user, unicode):
                    if db.users.count({'username':username_user}) != 1:
                        application.logger.debug('User not found')
                        response = {
                            'status': 'fail',
                            'message': 'no_user_found'
                        }
                        return make_response(jsonify(response)), 404

                    application.logger.debug('User found')
                    db.users.delete_one({'username':username_user})
                    response = {
                        'status': 'success',
                        'message': 'user_deleted'
                    }
                    return make_response(jsonify(response)), 200
            response = {
                'status': 'fail',
                'message': 'missing_token'
            }
            return make_response(jsonify(response)), 401
        except ExpiredTokenException as exc:
            application.logger.error("Expired token")
            response = {
                'status': 'fail',
                'message': 'expired_token'
            }
            return make_response(jsonify(response)), 401
        except InvalidTokenException as exc:
            application.logger.error("Invalid token")
            response = {
                'status': 'fail',
                'message': 'invalid_token'
            }
            return make_response(jsonify(response)), 401
        except Exception as exc:
            
            application.logger.error('Error msg: {0}. Error doc: {1}'.format(exc.message,exc.__doc__))
            response = {
                'status': 'fail',
                'message': 'internal_error'
            }
            return make_response(jsonify(response)),500 #pragma: no cover

#define the API resources
registration_view = RegisterAPI.as_view('registration_api')

#add Rules for API Endpoints
registration_blueprint.add_url_rule(
    '/users',
    view_func=registration_view,
    methods=['POST', 'DELETE']
)
