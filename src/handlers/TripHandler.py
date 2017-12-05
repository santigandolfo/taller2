"""Handlers related with trips"""

from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from schema import Schema, And, Use, SchemaError
from bson.objectid import ObjectId

from app import db, application
from src.models import User
from src.mixins.AuthenticationMixin import Authenticator
from src.mixins.TrackingMixin import TrackingTripsMixin
from src.services.push_notifications import send_push_notifications
from src.services.shared_server import register_trip, get_trips, estimate_trip_cost
import time

TRIPS_BLUEPRINT = Blueprint('trips', __name__)


class TripsAPI(MethodView):
    """Handler for trips related API"""

    @staticmethod
    def post(username):
        """Endpoint for starting a trip"""

        try:
            data = request.get_json()
            schema = Schema([{'request_id': And(Use(unicode), lambda x: ObjectId.is_valid(x))}])
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
                        location_initial = (result['coordinates']['latitude_initial'],result['coordinates']['longitude_initial'])
                        if TrackingTripsMixin.check_positions_with_location([result['driver'],result['rider']],location_initial):
                            db.requests.delete_one({'_id': ObjectId(requestID)})
                            result['start_time'] = time.time()
                            result['distance'] = 0.0
                            result_insertion = db.trips.insert_one(result)
                            message = "trip_started"
                            data = {}
                            send_push_notifications(result['rider'], message, data)
                            response = {
                                'status': 'success',
                                'message': 'trip_started',
                                'id': str(result_insertion.inserted_id)
                            }
                            status_code = 201
                        else:
                            response = {
                                'status': 'fail',
                                'message': 'users_not_in_start_location',
                            }
                            status_code = 200

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
                    location_final = (result['coordinates']['latitude_final'],result['coordinates']['longitude_final'])
                    if TrackingTripsMixin.check_positions_with_location([result['driver'],result['rider']],location_final):
                        db.trips.delete_one({'driver': username})
                        db.drivers.update_one({'username': username}, {'$set': {'trip': False}})
                        #TODO: Change hardcoded values
                        #Inform cost to users
                        coordinates = result['coordinates']
                        finish_time = time.time()
                        time_pickup = ( result['start_time'] - result['request_time'] ) / 60.0
                        time_travel = ( finish_time - result['start_time'] ) / 60.0
                        cost_data = {
                            "start_location": [coordinates['latitude_initial'], coordinates['longitude_initial']],
                            'end_location': [coordinates['latitude_final'], coordinates['longitude_final']],
                            "distance_in_km": result['distance'],
                            "time_pickup_in_min": time_pickup,
                            "time_travel_in_min": time_travel,
                            "pay_method": "credit",
                            "driver_id": User.get_user_by_username(username).uid,
                            "passenger_id": User.get_user_by_username(result['rider']).uid
                        }
                        resp = estimate_trip_cost(cost_data)
                        if resp.ok:
                            cost = resp.json()['value']
                            data = {
                                'start_location': [coordinates['latitude_initial'], coordinates['longitude_initial']],
                                'end_location': [coordinates['latitude_final'], coordinates['longitude_final']],
                                'distance': result['distance'],
                                'pay_method': 'credit',
                                'currency': '$',
                                'cost': cost,
                                'driver_id': User.get_user_by_username(username).uid,
                                'passenger_id': User.get_user_by_username(result['rider']).uid
                            }
                            resp = register_trip(data)
                            if resp.ok:
                                message = "trip_finished"
                                data = {
                                    'trip_ss_id': resp.json()['id'],
                                    'cost': cost
                                }
                                send_push_notifications(result['rider'], message, data)
                                response = {
                                    'status': 'success',
                                    'message': 'trip_finished',
                                    'trip_ss_id': resp.json()['id'],
                                    'cost': cost
                                }
                                status_code = 203
                            else:
                                response = resp.json()
                                status_code = resp.status_code
                        else:
                            response = resp.json()
                            status_code = resp.status_code
                    else:
                        response = {
                            'status': 'fail',
                            'message': 'users_not_in_final_location',
                        }
                        status_code = 200
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

    @staticmethod
    def get(username):
        """Endpoint for getting all the trips made by the user"""

        try:
            application.logger.info("{} asked for its trips".format(username))
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
                application.logger.info("User getting  trips: {}".format(token_username))
                user_id = db.users.find_one({"username": username})['uid']
                trips = get_trips(user_id)
                response = {
                    'status': 'success',
                    'message': 'trips_retrieved',
                    'trips': trips
                }
                status_code = 200
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
    methods=['POST', 'DELETE']
)

TRIPS_BLUEPRINT.add_url_rule(
    '/users/<username>/trip',
    view_func=TRIPS_VIEW,
    methods=['GET']
)
