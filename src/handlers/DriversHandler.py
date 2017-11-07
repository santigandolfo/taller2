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

    def patch(self,username):
        try:
            data = request.get_json() #TODO: Usar Schema para validar formato, deberia ser un bool
            try:
                availability = data['availability']
            except Exception as exc:
                response = {
                    'status': 'fail',
                    'message': 'missing_availability'
                }
                return make_response(jsonify(response)), 400
            application.logger.info("Asked to update driver's availability for: {}".format(username))
            if db.drivers.count({'username':username}) == 0:
                response = {
                    'status': 'fail',
                    'message': 'driver_not_found'
                }
                return make_response(jsonify(response)),404
            application.logger.info("driver {} exists".format(username))
            auth_header = request.headers.get('Authorization')
            if auth_header:
                auth_token = auth_header.split(" ")[1]
            else:
                auth_token = ''
            if auth_token:
                application.logger.info("Updating driver's availability w/ Auth: {}".format(auth_token))
                username_user = User.decode_auth_token(auth_token)
                application.logger.info("Update was requested by: {}".format(username_user))
                if username_user == username:
                    application.logger.info("Permission granted")
                    application.logger.info("driver to update {}".format(username_user))
                    db.drivers.find_one_and_update({'username':username},{'$set': {'available':availability}})
                    response = {
                        'status': 'success',
                        'message': 'updated_availability'
                    }
                    return make_response(jsonify(response)), 200
                else:
                    response = {
                        'status': 'fail',
                        'message': 'unauthorized_update'
                    }
                    return make_response(jsonify(response)), 401
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
            for driver in db.drivers.find({"available":True}):
                userId = db.users.find_one({"username":driver['username']})['uid']
                result.append(get_data(userId).json()) #TODO: Obtener toda la info con un solo request, pasando un vector de ids
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
    '/drivers/<username>',
    view_func=drivers_view,
    methods=['PATCH']
)

drivers_blueprint.add_url_rule(
    '/drivers/available',
    view_func=available_view,
    methods=['GET']
)
