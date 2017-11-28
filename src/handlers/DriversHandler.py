"""Handlers related with driver's specific functionality"""

from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from app import db, application
from src.models import User
from src.services.shared_server import get_data, register_car, delete_car
from src.mixins.AuthenticationMixin import Authenticator
from src.mixins.DriversMixin import DriversMixin

DRIVERS_BLUEPRINT = Blueprint('drivers', __name__)


class DriversAPI(MethodView):
    """Handler for drivers manipulation related API"""

    @staticmethod
    def patch(username):
        """Endpoint made for modifying the driver availability"""
        try:
            # TODO: Usar Schema para validar formato, deberia ser un bool
            data = request.get_json()
            availability = data.get('availability', '')
            if availability is not True and availability is not False:
                response = {
                    'status': 'fail',
                    'message': 'missing_availability'
                }
                return make_response(jsonify(response)), 400
            application.logger.info("Asked to update driver's availability for: {}"
                                    .format(username))
            if db.drivers.count({'username': username}) == 0:
                response = {
                    'status': 'fail',
                    'message': 'driver_not_found'
                }
                return make_response(jsonify(response)), 404
            application.logger.info("driver {} exists".format(username))
            auth_header = request.headers.get('Authorization')
            token_username, error_message = Authenticator.authenticate(auth_header)
            if error_message:
                response = {
                    'status': 'fail',
                    'message': error_message
                }
                return make_response(jsonify(response)), 401
            application.logger.info("Updating driver's availability w/ Auth: {}"
                                    .format(auth_header))
            application.logger.info("Update was requested by: {}".format(token_username))
            if token_username == username:
                application.logger.info("Permission granted")
                application.logger.info("driver to update {}".format(token_username))
                db.drivers.find_one_and_update({'username': username},
                                               {'$set': {'available': availability}})
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
            application.logger.error('Error msg: {0}. Error doc: {1}'
                                     .format(exc.message, exc.__doc__))
            response = {
                'status': 'fail',
                'message': 'internal_error',
                'error_description': exc.message
            }
            return make_response(jsonify(response)), 500


class CarRegisterEndPoint(MethodView):
    """View used for registering car information corresponding to a driver"""

    @staticmethod
    def post(username):
        """Registering a car for a specific driver"""
        try:
            data = request.get_json()
            application.logger.info("Asked to register driver's car information for: {}"
                                    .format(username))
            if db.drivers.count({'username': username}) == 0:
                response = {
                    'status': 'fail',
                    'message': 'driver_not_found'
                }
                return make_response(jsonify(response)), 404
            application.logger.info("driver {} exists".format(username))
            auth_header = request.headers.get('Authorization')
            token_username, error_message = Authenticator.authenticate(auth_header)
            if error_message:
                response = {
                    'status': 'fail',
                    'message': error_message
                }
                return make_response(jsonify(response)), 401
            application.logger.info("Registering driver's car information w/ Auth: {}"
                                    .format(auth_header))
            application.logger.info("Register was requested by: {}".format(token_username))
            if token_username == username:
                application.logger.info("Permission granted")
                application.logger.info("driver to update {}".format(token_username))
                user = User.get_user_by_username(username)
                resp = register_car(user.uid, data)
                if resp.ok:
                    response = {
                        'status': 'success',
                        'message': 'car_registered_succesfully',
                        'car_id': resp.json().get('id')
                    }
                    return make_response(jsonify(response)), 200
                else:
                    return make_response(jsonify(resp.json())), resp.status_code
            else:
                response = {
                    'status': 'fail',
                    'message': 'unauthorized_action'
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

class CarDeleteEndPoint(MethodView):
    """View used for deleting a car from a specific driver"""

    @staticmethod
    def delete(username,car_id):
        """Delete a car from a driver's info"""
        try:
            application.logger.info("Asked to remove driver's car information for: {}"
                                    .format(username))
            if db.drivers.count({'username': username}) == 0:
                response = {
                    'status': 'fail',
                    'message': 'driver_not_found'
                }
                return make_response(jsonify(response)), 404
            application.logger.info("driver {} exists".format(username))
            auth_header = request.headers.get('Authorization')
            token_username, error_message = Authenticator.authenticate(auth_header)
            if error_message:
                response = {
                    'status': 'fail',
                    'message': error_message
                }
                return make_response(jsonify(response)), 401
            application.logger.info("Removing driver's car information w/ Auth: {}"
                                    .format(auth_header))
            application.logger.info("Removal was requested by: {}".format(token_username))
            if token_username == username:
                application.logger.info("Permission granted")
                application.logger.info("driver to update {}".format(token_username))
                user = User.get_user_by_username(username)
                resp = delete_car(user.uid, car_id)
                if resp.ok:
                    response = {
                        'status': 'success',
                        'message': 'car_deleted_succesfully'
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

class AvailableEndpoint(MethodView):
    """View used for anything related with all drivers availability """

    @staticmethod
    def get():
        """Gets all the available drivers"""
        try:
            result = []
            for driver in DriversMixin.get_available_drivers():
                user_id = db.users.find_one({"username": driver})['uid']
                # TODO: Obtener toda la info con un solo request, pasando un vector de ids
                result.append(get_data(user_id).json())
            return make_response(jsonify(result)), 200
        except Exception as exc:  # pragma: no cover
            response = {
                'status': 'fail',
                'message': 'internal_error',
                'exc': exc.message
            }
            return make_response(jsonify(response)), 500


# define the API resources
DRIVERS_VIEW = DriversAPI.as_view('drivers_api')
AVAILABLE_VIEW = AvailableEndpoint.as_view('available_endpoint')
CAR_REGISTER_VIEW = CarRegisterEndPoint.as_view('car_register_endpoint')
CAR_DELETE_VIEW = CarDeleteEndPoint.as_view('car_delete_endpoint')

# add Rules for API Endpoints
DRIVERS_BLUEPRINT.add_url_rule(
    '/drivers/<username>',
    view_func=DRIVERS_VIEW,
    methods=['PATCH']
)

DRIVERS_BLUEPRINT.add_url_rule(
    '/drivers/<username>/cars',
    view_func=CAR_REGISTER_VIEW,
    methods=['POST']
)

DRIVERS_BLUEPRINT.add_url_rule(
    '/drivers/<username>/cars/<car_id>',
    view_func=CAR_DELETE_VIEW,
    methods=['DELETE']
)

DRIVERS_BLUEPRINT.add_url_rule(
    '/drivers/available',
    view_func=AVAILABLE_VIEW,
    methods=['GET']
)
