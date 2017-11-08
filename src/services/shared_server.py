import requests
from urlparse import urljoin
from app import SHARED_SERVER_URL, SS_TOKEN, application #application
from src.models import User


def register_user(userdata):
    return requests.post(urljoin(SHARED_SERVER_URL, 'users'), headers={"AuthToken":SS_TOKEN}, data=userdata)

def remove_user(user_id):
    return requests.delete(urljoin(SHARED_SERVER_URL, 'users/{}'.format(user_id)),headers={"AuthToken":SS_TOKEN})

def update_user_data(user_id,data):
    application.logger.info("About to call shared for users' data update with data {}, datatype: {}".format(str(data), type(data)))
    resp = requests.put(urljoin(SHARED_SERVER_URL,'users/{}'.format(user_id)), headers={"AuthToken":SS_TOKEN},json=data)
    application.logger.info("Response was {}".format(str(resp.content)))
    return resp

def validate_user(username, password):
    return requests.post(urljoin(SHARED_SERVER_URL,'users/validate'), headers={"AuthToken":SS_TOKEN}, json={'username': username, 'password': password})

def get_data(user_id):
    return requests.get(urljoin(SHARED_SERVER_URL,'users/{}'.format(user_id)),headers={"AuthToken":SS_TOKEN})
