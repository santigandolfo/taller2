from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from app import bcrypt, db, application
from src.models import  User
import python_jwt as jwt


login_blueprint = Blueprint('security', __name__)

class LoginAPI(MethodView):
    """Handler for login related API"""

    def post(self):

        try:
            data = request.get_json()
            email = data.get('email')
            if not email:
                response = {
                    'status': 'fail',
                    'message': 'invalid_email'
                }
                return make_response(jsonify(response)), 400
            application.logger.info("Login: {}".format(email))
            password = data.get('password')
            if not password:
                response = {
                    'status': 'fail',
                    'message': 'missing_password'
                }
                return make_response(jsonify(response)), 400
            application.logger.debug(type(email))
            search_pattern = {'email' : email}
            user = db.users.find_one(search_pattern)
            if not user:
                response = {
                    'status': 'fail',
                    'message': 'user_email_doesnt_exist'
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
            user = User(email,password)
            auth_token = user.encode_auth_token()
            application.logger.info(isinstance(auth_token,unicode))
            response = {
                'status': 'success',
                'message': 'login_succesful',
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



#define the API resources
login_view = LoginAPI.as_view('login_api')

#add Rules for API Endpoints
login_blueprint.add_url_rule(
    '/security',
    view_func=login_view,
    methods=['POST']
)
