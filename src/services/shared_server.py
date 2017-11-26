"""Services used from the shared server"""
import requests
from urlparse import urljoin
from app import SHARED_SERVER_URL, SS_TOKEN, application


def register_user(userdata):
    """Registers a user in the shared server"""
    return requests.post(urljoin(SHARED_SERVER_URL, 'users'),
                         headers={"AuthToken": SS_TOKEN}, data=userdata)


def remove_user(user_id):
    """Erases a user's account in the shared server"""

    return requests.delete(urljoin(SHARED_SERVER_URL, 'users/{}'.format(user_id)),
                           headers={"AuthToken": SS_TOKEN})


def update_user_data(user_id, data):
    """Update user's info in the shared server"""

    application.logger.info("About to call shared for users' data update with data {},"
                            " datatype: {}".format(str(data), type(data)))
    resp = requests.put(urljoin(SHARED_SERVER_URL, 'users/{}'.format(user_id)),
                        headers={"AuthToken": SS_TOKEN}, json=data)
    application.logger.info("Response was {}".format(str(resp.content)))
    return resp


def validate_user(username, password):
    """Validate user's credentials in the shared server"""

    return requests.post(urljoin(SHARED_SERVER_URL, 'users/validate'),
                         headers={"AuthToken": SS_TOKEN},
                         json={'username': username, 'password': password})


def get_data(user_id):
    """Get user's data from the shared server"""
    return requests.get(urljoin(SHARED_SERVER_URL, 'users/{}'.format(user_id)),
                        headers={"AuthToken": SS_TOKEN})
