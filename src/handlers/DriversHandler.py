import python_jwt as jwt
from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from app import db, application
from src.models import  User
from src.exceptions import BlacklistedTokenException, SignatureException, ExpiredTokenException, InvalidTokenException
from src.services.shared_server import get_data

drivers_blueprint = Blueprint('drivers', __name__)

class DriversAPI(MethodView):
    """Handler for drivers manipulation related API"""

    def patch(self):
        try:
            data = request.get_json()
            try:
                availability = data['availability']
            except Exception as exc:
                response = {
                    'status': 'fail',
                    'message': 'missing_availability'
                }
                return make_response(jsonify(response)), 400
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
                if availability and db.activedrivers.count({'uid':user.uid}) == 0:
                        db.activedrivers.insert_one({'uid':user.uid})
                if not availability and db.activedrivers.count({'uid':user.uid}) != 0:
                    try:
                        db.activedrivers.delete_one({'uid':user.uid})
                    except Exception:
                        pass
                response = {
                    'status': 'success',
                    'message': 'changed_availability'
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
        except Exception as exc: #pragma: no cover
            application.logger.error('Error msg: {0}. Error doc: {1}'.format(exc.message,exc.__doc__))
            response = {
                'status': 'fail',
                'message': 'internal_error',
                'error_description': exc.message
            }
            return make_response(jsonify(response)),500
    

class AvailableEndpoint(MethodView):
    def get(self):
        try:
            result = []
            for driver in db.activedrivers.find():
                result.append(get_data(driver['uid']).json())
            return make_response(jsonify(result)),200
        except Exception as exc: #pragma: no cover
            response = {
                'status': 'fail',
                'message': 'internal_error'
            }
            return make_response(jsonify(response)),500

#define the API resources
drivers_view = DriversAPI.as_view('drivers_api')
available_view = AvailableEndpoint.as_view('available_endpoint')

#add Rules for API Endpoints
drivers_blueprint.add_url_rule(
    '/drivers',
    view_func=drivers_view,
    methods=['PATCH']
)

drivers_blueprint.add_url_rule(
    '/drivers/available',
    view_func=available_view,
    methods=['GET']
)
