"""Custom exceptions"""
class InvalidTokenException(Exception):
    """ This generic exception raised on a invalid token"""

    def __init__(self, token, message=""):

        # Call the base class constructor with the parameters it needs
        super(InvalidTokenException, self).__init__(message)

        self.token = token


class BlacklistedTokenException(InvalidTokenException):
    """ This exception is raised if a token which is blacklisted is trying to be used """

    def __init__(self, token):

        # Call the base class constructor with the parameters it needs
        super(BlacklistedTokenException, self).__init__("This tokens is blacklisted", token)


class SignatureException(InvalidTokenException):
    """ This exception is raised if a token has not a valid signature"""

    def __init__(self, token):

        # Call the base class constructor with the parameters it needs
        super(SignatureException, self).__init__("Invalid signature", token)


class ExpiredTokenException(InvalidTokenException):
    """ This exception is raised if a token that is trying to be used has expired"""

    def __init__(self, token):

        # Call the base class constructor with the parameters it needs
        super(ExpiredTokenException, self).__init__("This token has expired", token)

