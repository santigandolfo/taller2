"""Handlers for manipulating the firebase token"""

from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from schema import Schema, Use, SchemaError

from app import db, application
from src.mixins.AuthenticationMixin import Authenticator
from src.models import User

TOKEN_MANIPULATION_BLUEPRINT = Blueprint('token_push_notifications', __name__)


class PushNotificationAPI(MethodView):
    """Handlers for manipulating the firebase token"""

    @staticmethod
    def put(username):
        """Endpoint for changing an user's push notification token"""
        try:
            data = request.get_json()
            schema = Schema([{'push_token': Use(unicode)}])
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
            application.logger.info("Updating user's push token w/ Auth: {}".format(auth_header))
            application.logger.info("Token decoded: Update was requested by: {}"
                                    .format(token_username))
            if token_username == username:
                application.logger.info("Permission granted")
                application.logger.info("User's position to update: {}".format(token_username))
                push_token = data['push_token']
                db.users.update_one({'username': username}, {'$set': {'push_token': push_token}})
                response = {
                    'status': 'success',
                    'message': 'push_token_updated'
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
TOKEN_MANIPULATION_VIEW = PushNotificationAPI.as_view('push_notification_api')

# add Rules for API Endpoints
TOKEN_MANIPULATION_BLUEPRINT.add_url_rule(
    '/users/<username>/push-token',
    view_func=TOKEN_MANIPULATION_VIEW,
    methods=['PUT']
)
