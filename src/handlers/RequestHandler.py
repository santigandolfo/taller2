"""Handlers related with rider's specific functionality"""

from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from schema import Schema, And, Use, SchemaError
from bson.objectid import ObjectId

from app import db, application
from src.mixins.AuthenticationMixin import Authenticator
from src.services.google_maps import get_directions
from src.services.push_notifications import send_push_notifications
from src.mixins.DriversMixin import DriversMixin

REQUESTS_BLUEPRINT = Blueprint('requests', __name__)


class RequestSubmission(MethodView):
    """Handler for request submission"""

    @staticmethod
    def post(username):
        """Endpoint for requesting a ride"""

        try:
            data = request.get_json()
            schema = Schema([{'latitude_initial': And(Use(float), lambda x: -90 < x < 90),
                              'latitude_final': And(Use(float), lambda x: -90 < x < 90),
                              'longitude_initial': And(Use(float), lambda x: -180 < x < 180),
                              'longitude_final': And(Use(float), lambda x: -180 < x < 180)}])

            # IMPORTANTE: el 0 es para que devuelva el diccionario dentro y no una lista
            data = schema \
                .validate([data])[0]
            application.logger.info("{} asked to submit a request for a trip".format(username))
            if db.riders.count({'username': username}) == 0:
                response = {
                    'status': 'fail',
                    'message': 'rider_not_found'
                }
                return make_response(jsonify(response)), 404
            application.logger.info("rider {} exists".format(username))
            auth_header = request.headers.get('Authorization')
            token_username, error_message = Authenticator.authenticate(auth_header)
            if error_message:
                response = {
                    'status': 'fail',
                    'message': error_message
                }
                return make_response(jsonify(response)), 401
            application.logger.info("Submitting trip request w/ Auth: {}".format(token_username))
            application.logger.info("Token decoded: {}".format(token_username))
            if token_username == username:
                application.logger.info("Permission granted")
                application.logger.info("Rider submitting request: {}".format(token_username))

                if db.requests.count({'rider': username}) == 0 and db.trips.count({'rider': username}) == 0:

                    assigned_driver = DriversMixin.get_closer_driver((data['latitude_initial'],                                                                  data['longitude_initial']))

                    if assigned_driver:
                        db.drivers.update_one({'username': assigned_driver}, {'$set': {'trip': True}})
                        application.logger.info("driver assigned")
                        directions_response = get_directions(data)
                        if not directions_response.ok:
                            raise Exception('failed_to_get_directions')
                        application.logger.info("google directions response:")
                        application.logger.info(directions_response)
                        if directions_response.json()['routes']:
                            directions = directions_response.json()['routes'][0]['overview_polyline']['points']
                        else:
                            raise Exception('unreachable_destination')
                        result = db.requests.insert_one({'rider': username, 'driver': assigned_driver, 'coordinates': data})
                        message = "A trip was assigned to you"
                        data = {
                            'rider': username,
                            'directions': directions,
                            'id': str(result.inserted_id)
                        }
                        send_push_notifications(assigned_driver, message, data)
                        response = {
                            'status': 'success',
                            'message': 'request_submitted',
                            'id': str(result.inserted_id),
                            'directions': directions,
                            'driver': assigned_driver
                        }
                        status_code = 201
                    else:
                        response = {
                            'status': 'fail',
                            'message': 'no_driver_available'
                        }
                        status_code = 404
                else:
                    response = {
                        'status': 'fail',
                        'message': 'request_or_trip_ongoing'
                    }
                    status_code = 409
            else:
                response = {
                    'status': 'fail',
                    'message': 'unauthorized_request'
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

class RequestCancellation(MethodView):
    """Handler for request cancellation"""

    @staticmethod
    def delete(requestID):
        """Endpoint for cancelling an unstarted trip a.k.a a request made that was matched"""

        try:
            auth_header = request.headers.get('Authorization')
            token_username, error_message = Authenticator.authenticate(auth_header)
            if error_message:
                response = {
                    'status': 'fail',
                    'message': error_message
                }
                return make_response(jsonify(response)), 401
            application.logger.info("Verifying token: {}".format(auth_header))
            application.logger.info("Cancellation was requested by: {}".format(token_username))
            result = db.requests.find_one({'_id': ObjectId(requestID)})
            if result:
                application.logger.info("Request found")
                driver_username = result['driver']
                application.logger.info("Request driver username: {}".format(driver_username))
                rider_username = result['rider']
                application.logger.info("Request rider username: {}".format(rider_username))
                if (token_username == driver_username or token_username == rider_username):
                    application.logger.info("Permission granted")
                    application.logger.info("User cancelling request: {}".format(token_username))
                    db.requests.delete_one({'_id': ObjectId(requestID)})
                    message = "Your trip was cancelled by " + token_username
                    if (token_username == driver_username):
                        receiver = rider_username
                    else:
                        receiver = driver_username
                    data = {
                        'id': requestID
                    }
                    send_push_notifications(receiver, message, data)
                    response = {
                        'status': 'success',
                        'message': 'request_cancelled'
                    }
                    status_code = 203
                else:
                    response = {
                        'status': 'fail',
                        'message': 'unauthorized_action'
                    }
                    status_code = 401
            else:
                response = {
                    'status': 'fail',
                    'message': 'no_request_found'
                }
                status_code = 404
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
REQUESTS_SUBMISSION_VIEW = RequestSubmission.as_view('request_submission')
REQUEST_CANCELLATION_VIEW = RequestCancellation.as_view('request_cancellation')

# add Rules for API Endpoints
REQUESTS_BLUEPRINT.add_url_rule(
    '/riders/<username>/request',
    view_func=REQUESTS_SUBMISSION_VIEW,
    methods=['POST']
)

REQUESTS_BLUEPRINT.add_url_rule(
    '/requests/<requestID>',
    view_func=REQUEST_CANCELLATION_VIEW,
    methods=['DELETE']
)
