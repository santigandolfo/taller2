import python_jwt as jwt
from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from app import db, application
from src.models import  User
from src.exceptions import BlacklistedTokenException, SignatureException, ExpiredTokenException, InvalidTokenException
from src.services.shared_server import get_data
from schema import Schema, And, Use, Optional, SchemaError

riders_blueprint = Blueprint('riders', __name__)

class RidersAPI(MethodView):
    """Handler for riders related API"""

    def post(self,username):
        try:
            data = request.get_json()
            schema = Schema([{'latitude_initial': And(Use(float), lambda x: -90 < x < 90),
                'latitude_final': And(Use(float), lambda x: -90 < x < 90),
                'longitude_initial':  And(Use(float), lambda x: -180 < x < 180),
                'longitude_final': And(Use(float), lambda x: -180 < x < 180)}])
            data = schema.validate([data])[0] #IMPORTANTE: el 0 es para que devuelva el diccionario dentro y no una lista

            application.logger.info("{} asked to submit a request for a trip".format(username))
            if db.riders.count({'username':username}) == 0:
                response = {
                    'status': 'fail',
                    'message': 'rider_not_found'
                }
                return make_response(jsonify(response)),404
            application.logger.info("rider {} exists".format(username))
            auth_header = request.headers.get('Authorization')
            if auth_header:
                auth_token = auth_header.split(" ")[1]
            else:
                auth_token = ''
            if auth_token:
                application.logger.info("Submitting trip request w/ Auth: {}".format(auth_token))
                username_user = User.decode_auth_token(auth_token)
                application.logger.info("Token decoded: {}".format(username_user))
                if username_user == username:
                    application.logger.info("Permission granted")
                    application.logger.info("Rider submitting request: {}".format(username_user))

                    if db.requests.count({'username':username,'pending':True}) == 0:
                        #DO REQUEST STUFF
                        result = db.requests.insert_one({'username':username,'coordinates':data,'pending':True})#TODO: Check this db
                        response = {
                        'status': 'success',
                        'message': 'request_submitted', #Add request id reference
                        'id': str(result.inserted_id)
                        }
                        return make_response(jsonify(response)), 201
                    else:
                        response = {
                        'status': 'fail',
                        'message': 'one_request_already_pending'
                        }
                        return make_response(jsonify(response)), 409
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
        except SchemaError as exc:
            application.logger.error("Request data error")
            response = {
                'status': 'fail',
                'message': 'bad_request_data'
            }
            return make_response(jsonify(response)), 400
        except ExpiredTokenException as exc:
            application.logger.error("Expired token")
            response = {
                'status': 'fail',
                'message': 'expired_token'
            }
            return make_response(jsonify(response)), 401
        except InvalidTokenException as exc:
            application.logger.error("Invalid token")
            response = {
                'status': 'fail',
                'message': 'invalid_token'
            }
            return make_response(jsonify(response)), 401
        except Exception as exc: #pragma: no cover
            application.logger.error('Error msg: {0}. Error doc: {1}'.format(exc.message,exc.__doc__))
            response = {
                'status': 'fail',
                'message': 'internal_error',
                'error_description': exc.message
            }
            return make_response(jsonify(response)),500

    def delete(self,username):
        try:
            application.logger.info("{} asked to delete pending request for a trip".format(username))
            if db.riders.count({'username':username}) == 0:
                response = {
                    'status': 'fail',
                    'message': 'rider_not_found'
                }
                return make_response(jsonify(response)),404
            application.logger.info("rider {} exists".format(username))
            auth_header = request.headers.get('Authorization')
            if auth_header:
                auth_token = auth_header.split(" ")[1]
            else:
                auth_token = ''
            if auth_token:
                application.logger.info("Verifying token: {}".format(auth_token))
                username_user = User.decode_auth_token(auth_token)
                application.logger.info("Deletion was requested by: {}".format(username_user))
                if username_user == username:
                    application.logger.info("Permission granted")
                    if db.requests.count({'username':username,'pending':True}) > 0:
                        result = db.requests.delete_one({'username':username,'pending':True})
                        response = {
                        'status': 'success',
                        'message': 'request_cancelled',
                        'count': result.deleted_count #should be always 1
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
                        'message': 'unauthorized_request'
                    }
                    return make_response(jsonify(response)), 401
            response = {
                'status': 'fail',
                'message': 'missing_token'
            }
            return make_response(jsonify(response)), 401
        except SchemaError as exc:
            application.logger.error("Request data error")
            response = {
                'status': 'fail',
                'message': 'bad_request_data'
            }
            return make_response(jsonify(response)), 400
        except ExpiredTokenException as exc:
            application.logger.error("Expired token")
            response = {
                'status': 'fail',
                'message': 'expired_token'
            }
            return make_response(jsonify(response)), 401
        except InvalidTokenException as exc:
            application.logger.error("Invalid token")
            response = {
                'status': 'fail',
                'message': 'invalid_token'
            }
            return make_response(jsonify(response)), 401
        except Exception as exc: #pragma: no cover
            application.logger.error('Error msg: {0}. Error doc: {1}'.format(exc.message,exc.__doc__))
            response = {
                'status': 'fail',
                'message': 'internal_error',
                'error_description': exc.message
            }
            return make_response(jsonify(response)),500




#define the API resources
riders_view = RidersAPI.as_view('riders_api')


#add Rules for API Endpoints
riders_blueprint.add_url_rule(
    '/riders/<username>/request',
    view_func=riders_view,
    methods=['POST','DELETE']
)
