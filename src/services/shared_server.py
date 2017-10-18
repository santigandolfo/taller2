import requests
from urlparse import urljoin
from app import SHARED_SERVER_URL, application
from src.models import User




def register_user(userdata):
    return requests.post(urljoin(SHARED_SERVER_URL, 'users'), data=userdata)

def remove_user(user_id, auth_token):
    return requests.delete(urljoin(SHARED_SERVER_URL, 'users/{}'.format(user_id)),header={"Authentication":auth_token})

def update_user_data(user_id,auth_token,data):
    return requests.put(urljoin(SHARED_SERVER_URL, 'users/{}'.format(user_id)),header={"Authentication":auth_token})    

def validate_user(username, password):
    return requests.post(urljoin(SHARED_SERVER_URL,'users/validate'), data={'username': username, 'password': password})

def get_data(user_id):
    return requests.get(urljoin(SHARED_SERVER_URL, 'users/{}'.format(user_id)))