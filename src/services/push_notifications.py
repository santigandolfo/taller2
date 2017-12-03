import os
from src.models import User
from pyfcm import FCMNotification
from app import application


FIREBASE_KEY = os.environ["FIREBASE_KEY"]


def send_push_notifications(username, message_body, data_message):
    application.logger.info("Sending push notification to user: {}".format(username))
    user = User.get_user_by_username(username)
    try:
        push_service = FCMNotification(api_key=FIREBASE_KEY)
        registration_id = user.push_token
        application.logger.info("Sending push notification to user registered with firebase id: {}".format(registration_id))
        result = push_service.notify_single_device(registration_id=registration_id,
                                                    message_body=message_body,
                                                    data_message=data_message)
        application.logger.info("Result of push notification: ")
        application.logger.info(result)
        return result
    except:
        pass
