"""Handlers related with rider's specific functionality"""

from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from schema import Schema, And, Use, SchemaError

from app import db, application
from src.mixins.AuthenticationMixin import Authenticator

RIDERS_BLUEPRINT = Blueprint('riders', __name__)


class RidersAPI(MethodView):
    """Handler for riders related API"""

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
            data = schema\
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

                if db.requests.count({'username': username, 'pending': True}) == 0:
                    # DO REQUEST STUFF
                    result = db.requests.insert_one(
                        {'username': username, 'coordinates': data, 'pending': True})
                    response = {
                        'status': 'success',
                        'message': 'request_submitted',  # Add request id reference
                        'id': str(result.inserted_id)
                    }
                    status_code = 201
                else:
                    response = {
                        'status': 'fail',
                        'message': 'one_request_already_pending'
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

    @staticmethod
    def delete(username):
        """Endpoint for canceling a requested a ride"""

        try:
            application.logger.info("{} asked to delete pending request for a trip"
                                    .format(username))
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
            application.logger.info("Verifying token: {}".format(auth_header))
            application.logger.info("Deletion was requested by: {}".format(token_username))
            if token_username == username:
                application.logger.info("Permission granted")
                if db.requests.count({'username': username, 'pending': True}) > 0:
                    result = db.requests.delete_many({'username': username, 'pending': True})
                    response = {
                        'status': 'success',
                        'message': 'request_cancelled',
                        'count': result.deleted_count  # should be always 1
                    }
                    return make_response(jsonify(response)), 200
                else:
                    response = {
                        'status': 'fail',
                        'message': 'no_pending_request'
                    }
                    return make_response(jsonify(response)), 404
            else:
                response = {
                    'status': 'fail',
                    'message': 'unauthorized_deletion'
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


# define the API resources
RIDERS_VIEW = RidersAPI.as_view('riders_api')

# add Rules for API Endpoints
RIDERS_BLUEPRINT.add_url_rule(
    '/riders/<username>/request',
    view_func=RIDERS_VIEW,
    methods=['POST', 'DELETE']
)
