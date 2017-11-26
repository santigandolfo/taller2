from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from app import db, application
from src.services.shared_server import get_data
from src.mixins.AuthenticationMixin import Authenticator

drivers_blueprint = Blueprint('drivers', __name__)


class DriversAPI(MethodView):
    """Handler for drivers manipulation related API"""

    @staticmethod
    def patch(username):
        try:
            data = request.get_json()  # TODO: Usar Schema para validar formato, deberia ser un bool
            availability = data.get('availability', '')
            if availability is not True and availability is not False:
                response = {
                    'status': 'fail',
                    'message': 'missing_availability'
                }
                return make_response(jsonify(response)), 400
            application.logger.info("Asked to update driver's availability for: {}".format(username))
            if db.drivers.count({'username': username}) == 0:
                response = {
                    'status': 'fail',
                    'message': 'driver_not_found'
                }
                return make_response(jsonify(response)), 404
            application.logger.info("driver {} exists".format(username))
            auth_header = request.headers.get('Authorization')
            token_username, error_message = Authenticator.authenticate(auth_header)
            print "Error message: (" + error_message + ")" \
                                                       ""
            if error_message:
                response = {
                    'status': 'fail',
                    'message': error_message
                }
                return make_response(jsonify(response)), 401
            application.logger.info("Updating driver's availability w/ Auth: {}".format(auth_header))
            application.logger.info("Update was requested by: {}".format(token_username))
            if token_username == username:
                application.logger.info("Permission granted")
                application.logger.info("driver to update {}".format(token_username))
                db.drivers.find_one_and_update({'username': username}, {'$set': {'available': availability}})
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
        except Exception as exc:  # pragma: no cover
            application.logger.error('Error msg: {0}. Error doc: {1}'.format(exc.message, exc.__doc__))
            response = {
                'status': 'fail',
                'message': 'internal_error',
                'error_description': exc.message
            }
            return make_response(jsonify(response)), 500


class AvailableEndpoint(MethodView):
    @staticmethod
    def get():
        try:
            result = []
            for driver in db.drivers.find({"available": True}):
                user_id = db.users.find_one({"username": driver['username']})['uid']
                # TODO: Obtener toda la info con un solo request, pasando un vector de ids
                result.append(get_data(user_id).json())
            return make_response(jsonify(result)), 200
        except Exception:  # pragma: no cover
            response = {
                'status': 'fail',
                'message': 'internal_error'
            }
            return make_response(jsonify(response)), 500


# define the API resources
drivers_view = DriversAPI.as_view('drivers_api')
available_view = AvailableEndpoint.as_view('available_endpoint')

# add Rules for API Endpoints
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
