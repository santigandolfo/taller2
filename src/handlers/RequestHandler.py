from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView

from app import db, application
from src.exceptions import ExpiredTokenException, InvalidTokenException
from src.models import User
from src.services.shared_server import get_data

requests_blueprint = Blueprint('requests', __name__)


class RequestsAvailable(MethodView):
    """Handler for requests available service"""

    @staticmethod
    def get():
        try:
            application.logger.info("asked to see all the requests available")
            auth_header = request.headers.get('Authorization')
            if auth_header:
                auth_token = auth_header.split(" ")[1]
            else:
                auth_token = ''
            if auth_token:
                application.logger.info("Token: {}".format(auth_token))
                username_user = User.decode_auth_token(auth_token)
                application.logger.info("Token decoded: {}".format(username_user))
                if db.drivers.count({'username': username_user}) > 0:
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
            response = {
                'status': 'fail',
                'message': 'missing_token'
            }
            return make_response(jsonify(response)), 401
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
            return make_response(jsonify(response)), 500


# define the API resources
requests_available_view = RequestsAvailable.as_view('requests_available')

# add Rules for API Endpoints
requests_blueprint.add_url_rule(
    '/requests/available',
    view_func=requests_available_view,
    methods=['GET']
)
