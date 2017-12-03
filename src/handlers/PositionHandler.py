"""Handlers related with the position of users"""

from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from schema import Schema, And, Use, SchemaError

from app import db, application
from src.mixins.AuthenticationMixin import Authenticator
from src.models import User

POSITION_BLUEPRINT = Blueprint('position', __name__)


class PositionAPI(MethodView):
    """Handler for position related API"""

    @staticmethod
    def put(username):
        """Endpoint for Updating a user position"""
        try:
            data = request.get_json()
            schema = Schema([{'latitude': And(Use(float), lambda x: -90 < x < 90),
                              'longitude': And(Use(float), lambda x: -180 < x < 180)}])
            # IMPORTANTE: el 0 es para que devuelva el diccionario dentro y no una lista
            data = schema.validate([data])[0]
            application.logger.info("Asked to update {}'s position coordinates'".format(username))
            user = User.get_user_by_username(username)
            if not user:
                response = {
                    'status': 'fail',
                    'message': 'user_not_found'
                }
                return make_response(jsonify(response)), 404
            application.logger.info("user {} exists".format(username))
            auth_header = request.headers.get('Authorization')
            token_username, error_message = Authenticator.authenticate(auth_header)
            if error_message:
                response = {
                    'status': 'fail',
                    'message': error_message
                }
                return make_response(jsonify(response)), 401
            application.logger.info("Updating user's coordinates w/ Auth: {}".format(auth_header))
            application.logger.info("Token decoded: Update was requested by: {}"
                                    .format(token_username))
            if token_username == username:
                application.logger.info("Permission granted")
                application.logger.info("User's position to update: {}".format(token_username))
                latitude = data['latitude']
                longitude = data['longitude']
                if db.positions.count({'username': username}) == 0:
                    db.positions.insert_one({'username': username, 'latitude': latitude,
                                             'longitude': longitude})
                else:
                    db.positions.find_one_and_update({'username': username},
                                                     {'$set': {'latitude': latitude,
                                                               'longitude': longitude}})
                response = {
                    'status': 'success',
                    'message': 'position_updated'
                }
                return make_response(jsonify(response)), 200
            response = {
                'status': 'fail',
                'message': 'unauthorized_update'
            }
            return make_response(jsonify(response)), 401

        except SchemaError:
            application.logger.error("Request data error")
            response = {
                'status': 'fail',
                'message': 'bad_request_data'
            }
            return make_response(jsonify(response)), 400

        except Exception as exc:  # pragma: no cover
            application.logger.error('Error msg: {0}. Error doc: {1}'.
                                     format(exc.message, exc.__doc__))
            response = {
                'status': 'fail',
                'message': 'internal_error',
                'error_description': exc.message
            }
            return make_response(jsonify(response)), 500


# define the API resources
POSITION_VIEW = PositionAPI.as_view('position_api')

# add Rules for API Endpoints
POSITION_BLUEPRINT.add_url_rule(
    '/users/<username>/coordinates',
    view_func=POSITION_VIEW,
    methods=['PUT']
)
