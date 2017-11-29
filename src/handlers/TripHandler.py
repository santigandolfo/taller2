"""Handlers related with trips"""

from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from schema import Schema, And, Use, SchemaError
from bson.objectid import ObjectId

from app import db, application
from src.mixins.AuthenticationMixin import Authenticator
from src.services.push_notifications import send_push_notifications


TRIPS_BLUEPRINT = Blueprint('trips', __name__)


class TripsAPI(MethodView):
    """Handler for trips related API"""

    @staticmethod
    def post(username):
        """Endpoint for starting a trip"""

        try:
            data = request.get_json()
            schema = Schema([{'request_id': And(Use(unicode), lambda x: ObjectId.is_valid(x) ) }])
            # IMPORTANTE: el 0 es para que devuelva el diccionario dentro y no una lista
            data = schema \
                .validate([data])[0]
            requestID = data['request_id']
            application.logger.info("{} asked to start a trip".format(username))
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
            application.logger.info("Token decoded: {}".format(token_username))
            if token_username == username:
                application.logger.info("Permission granted")
                application.logger.info("Driver starting trip: {}".format(token_username))
                result = db.requests.find_one({'_id': ObjectId(requestID)})
                if result:
                    if result['driver'] == username:
                        db.requests.delete_one({'_id': ObjectId(requestID)})
                        result = db.trips.insert_one(result)
                        response = {
                            'status': 'success',
                            'message': 'trip_started',
                            'id': str(result.inserted_id)
                        }
                        status_code = 201
                    else:
                        response = {
                            'status': 'fail',
                            'message': 'unauthorized_for_request'
                        }
                        status_code = 401
                else:
                    response = {
                        'status': 'fail',
                        'message': 'request_not_found'
                    }
                    status_code = 404
            else:
                response = {
                    'status': 'fail',
                    'message': 'unauthorized_action'
                }
                status_code = 401
            return make_response(jsonify(response)), status_code
        except SchemaError:
            application.logger.error("Request data error")
            response = {
                'status': 'fail',
                'message': 'bad_request_data'
            }
            return make_response(jsonify(response)), 400
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
    def delete(username):
        """Endpoint for finishing an ongoing trip"""

        try:
            application.logger.info("{} asked to finish a trip".format(username))
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
            application.logger.info("Token decoded: {}".format(token_username))
            if token_username == username:
                application.logger.info("Permission granted")
                application.logger.info("Driver finishing trip: {}".format(token_username))
                result = db.trips.find_one({'driver': username})
                if result:
                    db.trips.delete_one({'driver': username})
                    #TODO: Inform trip to Shared Server
                    #Inform cost to users
                    response = {
                        'status': 'success',
                        'message': 'trip_finished'
                    }
                    status_code = 203
                else:
                    response = {
                        'status': 'fail',
                        'message': 'trip_not_found'
                    }
                    status_code = 404
            else:
                response = {
                    'status': 'fail',
                    'message': 'unauthorized_action'
                }
                status_code = 401
            return make_response(jsonify(response)), status_code
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
TRIPS_VIEW = TripsAPI.as_view('trips_api')

# add Rules for API Endpoints
TRIPS_BLUEPRINT.add_url_rule(
    '/drivers/<username>/trip',
    view_func=TRIPS_VIEW,
    methods=['POST','DELETE']
)
