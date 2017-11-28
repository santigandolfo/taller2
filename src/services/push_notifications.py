import requests
import os
from src.models import User

FIREBASE_KEY = os.environ["FIREBASE_KEY"]


def send_push_notifications(username, message):
    user = User.get_user_by_username(username)
    parameters = {
        'to': user['push_token'],
        'message': message
    }
    return requests.post("https://maps.googleapis.com/maps/api/directions/json",
                         json=parameters,
                         Authorization=FIREBASE_KEY)