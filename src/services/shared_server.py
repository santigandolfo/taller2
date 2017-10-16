import requests
from urlparse import urljoin
from app import SHARED_SERVER_URL, application
from src.models import User




def register_user(userdata):
    return requests.post(urljoin(SHARED_SERVER_URL, 'users'), data=userdata)


def get_user_data(user):
    return requests.get(urljoin(SHARED_SERVER_URL,'users/{}'.format(user.id)))

def validate_user(user):
    return requests.get(urljoin(SHARED_SERVER_URL,'users/validate'), data={'username': user.username, 'password': user.password})
