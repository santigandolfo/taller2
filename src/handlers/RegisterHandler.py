
from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from app import bcrypt, db, application
from logging import StreamHandler
from src.models import  User


registration_blueprint = Blueprint('users', __name__)

class RegisterAPI(MethodView):
    """Handler for registration related API"""

    def post(self):

        try:
            data = request.get_json()
            email = data.get('email')
            application.logger.info("Registration: {}".format(email))
            password = data.get('password')
        except Exception as exc:
            response = {
                'status': 'fail',
                'message': 'bad_request'
            }
            return make_response(jsonify(response)), 400
    
        try:
            search_pattern = {'email' : email}
            if db.users.count(search_pattern) > 0:
                response = {
                    'status': 'fail',
                    'message': 'user_email_already_exists'
                }
                return make_response(jsonify(response)), 409

            application.logger.debug('User not found while registering.OK')
            user = User(email=email,password=password)
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
            application.logger.error("Error ocurred. Message: "+exc.message+ ".Doc: "+ exc.__doc__)
            response = {
                'status': 'fail',
                'message': 'internal_error',
                'error_de': exc.message
            }
            return make_response(jsonify(response)), 500
    
    def delete(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        search_pattern = {'email' : email}
        response = {
                'status': 'fail',
                'message': 'user_email_already_exists'
            }
        return make_response(jsonify(data)), 200
        if db.users.find({},search_pattern).count > 0:
            response = {
                'status': 'fail',
                'message': 'user_email_already_exists'
            }
            return make_response(jsonify(response)), 409


        try:
            db.users.insert_one({'email': email, 'password': password})
            response = {
                'status': 'succes',
                'message': 'user_registered',
                'auth_token': 'TODO'
            }
            return make_response(jsonify(response)),200
        except Exception as exc:
            response = {
                'status': 'fail',
                'message': 'internal_error'
            }
            return make_response(jsonify(response)),500
    
#define the API resources
registration_view = RegisterAPI.as_view('registration_api')

#add Rules for API Endpoints
registration_blueprint.add_url_rule(
    '/users',
    view_func=registration_view,
    methods=['POST', 'DELETE']
)