import python_jwt as jwt
from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from app import db, application
from src.models import  User
from src.exceptions import BlacklistedTokenException, SignatureException, ExpiredTokenException, InvalidTokenException
from src.services.shared_server import register_user, remove_user, update_user_data

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
            resp = register_user(data)
            if resp.ok:
                application.logger.info('User registered')
                user = User(username=username,uid=resp.json()['user'].get('id'),ss_token=resp.json()['auth_token'])
                db.users.insert_one(user.__dict__)
                auth_token = user.encode_auth_token()
                application.logger.debug(isinstance(auth_token,unicode))
                response = {
                    'status': 'success',
                    'message': 'user_registered',
                    'auth_token': auth_token,
                    'info': resp.json().get('user')
                }
                application.logger.debug('Generated json correctly')
                return make_response(jsonify(response)), 201
            else:
                return make_response(jsonify(resp.json())), resp.status_code
        except Exception as exc:
            application.logger.error("Error ocurred. Message: {} .Doc: {}".format(exc.message, exc.__doc__))
            response = {
                'status': 'fail',
                'message': 'internal_error',
                'error_description': exc.message
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
                user = User.get_user_by_username(username_user)
                if  isinstance(username_user, unicode):
                    
                    application.logger.debug('User found')
                    resp = remove_user(user.uid,user.ss_token)
                    if resp.ok:
                        response = {
                            'status': 'success',
                            'message': 'user_deleted'
                        }
                        user.remove_from_db()
                        return make_response(jsonify(response)), 203
                    else:
                        return make_response(jsonify(resp.json())), resp.status_code
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
        except Exception as exc: #pragma: no cover
            
            application.logger.error('Error msg: {0}. Error doc: {1}'.format(exc.message,exc.__doc__))
            response = {
                'status': 'fail',
                'message': 'internal_error',
                'error_description': exc.message
            }
            return make_response(jsonify(response)),500 

    def put(self):
        try:
            data = request.get_json()
            auth_header = request.headers.get('Authorization')
            if auth_header:
                auth_token = auth_header.split(" ")[1]
            else:
                auth_token = ''
            application.logger.info("Removing user. Auth: {}".format(auth_token))
            if auth_token:
                username_user = User.decode_auth_token(auth_token)
                user = User.get_user_by_username(username_user)
                if not user:
                    response = {
                        'status': 'fail',
                        'message': 'no_such_user'
                    }
                    return make_response(jsonify(response)),404
                resp = update_user_data(user.uid,user.ss_token,data)
                if resp.ok:
                    response = {
                        'status': 'success',
                        'message': 'data_changed_succesfully'
                    }
                    return make_response(jsonify(response)), 200
                else:
                    return make_response(jsonify(resp.json())), resp.status_code
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
        except Exception as exc: #pragma: no cover
            application.logger.error('Error msg: {0}. Error doc: {1}'.format(exc.message,exc.__doc__))
            response = {
                'status': 'fail',
                'message': 'internal_error',
                'error_description': exc.message
            }
            return make_response(jsonify(response)),500 

#define the API resources
registration_view = RegisterAPI.as_view('registration_api')

#add Rules for API Endpoints
registration_blueprint.add_url_rule(
    '/users',
    view_func=registration_view,
    methods=['POST', 'DELETE', 'PUT']
)
