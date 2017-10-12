from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from app import bcrypt, db, application
from src.models import  User, BlacklistToken
import python_jwt as jwt


security_blueprint = Blueprint('security', __name__)

class SecurityAPI(MethodView):
    """Handler for login/logout related API"""
    # LOGIN
    def post(self):

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
            search_pattern = {'username' : username}
            user = db.users.find_one(search_pattern)
            if not user:
                response = {
                    'status': 'fail',
                    'message': 'unregistered_user'
                }
                return make_response(jsonify(response)), 409
            application.logger.info("Login: user exists")
            if not bcrypt.check_password_hash(user['password'], password):
                response = {
                    'status': 'fail',
                    'message': 'wrong_password'
                }
                return make_response(jsonify(response)), 401
            application.logger.info("Login: password OK")
            user = User(username,password)
            auth_token = user.encode_auth_token()
            application.logger.info(isinstance(auth_token,unicode))
            response = {
                'status': 'success',
                'message': 'login_succesful',
                'auth_token': auth_token
            }
            application.logger.debug('Generated json correctly')
            return make_response(jsonify(response)), 201

        except Exception as exc: #pragma: no cover
            application.logger.error("Error ocurred. Message: "+exc.message+ ".Doc: "+ exc.__doc__)
            response = {
                'status': 'fail',
                'message': 'internal_error',
                'error_de': exc.message
            }
            return make_response(jsonify(response)), 500
    # LOGOUT
    def delete(self):
        try:
            auth_header = request.headers.get('Authorization')
            if auth_header:
                auth_token = auth_header.split(" ")[1]
            else:
                auth_token = ''
            application.logger.debug("Log Out: {}".format(auth_token))
            if auth_token:
                try:
                    username_user = User.decode_auth_token(auth_token)
                except Exception as exc:
                    if exc.message == 'expired':
                        response = {
                            'status': 'fail',
                            'message': 'expired_token'
                        }
                        return make_response(jsonify(response)),401
                    response = {
                        'status': 'fail',
                        'message': 'invalid_token'
                    }
                    return make_response(jsonify(response)),401

                application.logger.info("Log Out: {}".format(username_user))
                blacklist_token = BlacklistToken(token=auth_token)
                application.logger.debug("blacklistToken created")
                db.blacklistedTokens.insert_one(blacklist_token.__dict__)
                application.logger.debug("blacklistToken inserted")
                responseObject = {
                    'status': 'success',
                    'message': 'logout_succesful'
                }
                return make_response(jsonify(responseObject)), 200
            else:
                responseObject = {
                    'status': 'fail',
                    'message': 'missing_token'
                }
                return make_response(jsonify(responseObject)), 400
        except Exception as exc:
            application.logger.error('Error msg: {0}. Error doc: {1}'.format(exc.message,exc.__doc__))
            response = {
                'status': 'fail',
                'message': 'internal_error'
            }
            return make_response(jsonify(response)),500

#define the API resources
security_view = SecurityAPI.as_view('security_api')

#add Rules for API Endpoints
security_blueprint.add_url_rule(
    '/security',
    view_func=security_view,
    methods=['POST', 'DELETE']
)
