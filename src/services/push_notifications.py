import requests
import os
from src.models import User

FIREBASE_KEY = os.environ["FIREBASE_KEY"]


def send_push_notifications(username, message, additional_data):
    user = User.get_user_by_username(username)
    try:
        additional_data['to'] = user['push_token']
        additional_data['message'] = message
        return requests.post("https://maps.googleapis.com/maps/api/directions/json",
                         json=additional_data,
                         Authorization=FIREBASE_KEY)
    except:
        pass
