from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from schema import Schema, And, Use, SchemaError

from app import db, application
from src.exceptions import ExpiredTokenException, InvalidTokenException
from src.models import User

position_blueprint = Blueprint('position', __name__)


class PositionAPI(MethodView):
    """Handler for position related API"""

    @staticmethod
    def put(username):
        try:
            data = request.get_json()
            schema = Schema([{'latitude': And(Use(float), lambda x: -90 < x < 90),
                              'longitude':  And(Use(float), lambda x: -180 < x < 180)}])
            # IMPORTANTE: el 0 es para que devuelva el diccionario dentro y no una lista
            data = schema.validate([data])[0]
            application.logger.info("Asked to update {}'s position coordinates'".format(username))
            user = User.get_user_by_username(username)
            if not user:
                response = {
                    'status': 'fail',
                    'message': 'user_not_found'
                }
                return make_response(jsonify(response)),404
            application.logger.info("user {} exists".format(username))
            auth_header = request.headers.get('Authorization')
            if auth_header:
                auth_token = auth_header.split(" ")[1]
            else:
                auth_token = ''
            if auth_token:
                application.logger.info("Updating user's coordinates w/ Auth: {}".format(auth_token))
                username_user = User.decode_auth_token(auth_token)
                application.logger.info("Token decoded: Update was requested by: {}".format(username_user))
                if username_user == username:
                    application.logger.info("Permission granted")
                    application.logger.info("User's position to update: {}".format(username_user))
                    latitude = data['latitude']
                    longitude = data['longitude']
                    if db.positions.count({'username': username}) == 0:  # TODO: Asegurarse que ya este inicializado
                        db.positions.insert_one({'username': username, 'latitude': latitude, 'longitude': longitude})
                    else:
                        db.positions.find_one_and_update({'username': username}, {'$set': {'latitude': latitude},
                                                                                  '$set': {'longitude': longitude}})
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
            response = {
                'status': 'fail',
                'message': 'missing_token'
            }
            return make_response(jsonify(response)), 401

        except SchemaError:
            application.logger.error("Request data error")
            response = {
                'status': 'fail',
                'message': 'bad_request_data'
            }
            return make_response(jsonify(response)), 400
        except ExpiredTokenException:
            application.logger.error("Expired token")
            response = {
                'status': 'fail',
                'message': 'expired_token'
            }
            return make_response(jsonify(response)), 401
        except InvalidTokenException:
            application.logger.error("Invalid token")
            response = {
                'status': 'fail',
                'message': 'invalid_token'
            }
            return make_response(jsonify(response)), 401
        except Exception as exc:  # pragma: no cover
            application.logger.error('Error msg: {0}. Error doc: {1}'.format(exc.message, exc.__doc__))
            response = {
                'status': 'fail',
                'message': 'internal_error',
                'error_description': exc.message
            }
            return make_response(jsonify(response)),500


# define the API resources
position_view = PositionAPI.as_view('position_api')

# add Rules for API Endpoints
position_blueprint.add_url_rule(
    '/users/<username>/coordinates',
    view_func=position_view,
    methods=['PUT']
)
