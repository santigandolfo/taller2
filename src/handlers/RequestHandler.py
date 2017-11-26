"""Handlers related with requested rides"""

from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView

from app import db, application
from src.mixins.AuthenticationMixin import Authenticator
from src.services.shared_server import get_data

REQUESTS_BLUEPRINT = Blueprint('requests', __name__)


class RequestsAvailable(MethodView):
    """Handler for requests available service"""

    @staticmethod
    def get():
        """Get all pending requests"""
        try:
            application.logger.info("asked to see all the requests available")
            auth_header = request.headers.get('Authorization')
            token_username, error_message = Authenticator.authenticate(auth_header)
            if error_message:
                response = {
                    'status': 'fail',
                    'message': error_message
                }
                return make_response(jsonify(response)), 401
            application.logger.info("Token: {}".format(auth_header))
            application.logger.info("Token decoded: {}".format(token_username))
            if db.drivers.count({'username': token_username}) > 0:
                application.logger.info("Permission granted")
                pipeline = [
                    {"$match": {"pending": True}},
                    {"$project": {"username": "$username", "coordinates": "$coordinates"}}
                ]
                results = []
                for doc in db.requests.aggregate(pipeline):
                    result = {}
                    user_id = db.users.find_one({"username": doc['username']})['uid']
                    result['userData'] = get_data(user_id).json()
                    result['coordinates'] = doc['coordinates']
                    results.append(result)
                return make_response(jsonify(results)), 200
            else:
                response = {
                    'status': 'fail',
                    'message': 'unauthorized_request'
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
REQUESTS_AVAILABLE_VIEW = RequestsAvailable.as_view('requests_available')

# add Rules for API Endpoints
REQUESTS_BLUEPRINT.add_url_rule(
    '/requests/available',
    view_func=REQUESTS_AVAILABLE_VIEW,
    methods=['GET']
)
