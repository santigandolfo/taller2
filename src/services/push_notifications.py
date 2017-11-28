import requests
import os
from src.models import User
from pyfcm import FCMNotification


FIREBASE_KEY = os.environ["FIREBASE_KEY"]


def send_push_notifications(username, message_body, data_message):
    user = User.get_user_by_username(username)
    try:
        push_service = FCMNotification(api_key=FIREBASE_KEY)
        registration_id = user['push_token']
        result = push_service.notify_single_device(registration_id=registration_id,
                                                    message_body=message_body,
                                                    data_message=data_message)
        return result
    except:
        pass
