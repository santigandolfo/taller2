from src.models import User
from src.exceptions import InvalidTokenException, ExpiredTokenException
from app import application


class Authenticator:

    def __init__(self):
        application.loggger.info("Authenticator initialized")

    @staticmethod
    def authenticate(auth_header):
        error_message = ''
        username = ''
        try:
            if auth_header and len(auth_header.split(" ")) == 2 and auth_header.split(" ")[1]:
                auth_token = auth_header.split(" ")[1]
                username = User.decode_auth_token(auth_token)
            else:
                application.logger.info("Missing token")
                error_message = 'missing_token'

        except ExpiredTokenException:
            application.logger.info("Expired token")
            error_message = 'expired_token'

        except InvalidTokenException:
            application.logger.info("Invalid token")
            error_message = 'invalid_token'

        return username, error_message
