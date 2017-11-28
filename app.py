import os
import logging
import sys
from flask import Flask, jsonify
from pymongo import MongoClient
from logging import StreamHandler
import requests
from urlparse import urljoin


application = Flask(__name__)

DB_URL = os.environ["DB_URL"]
DB_NAME = os.environ["DB_NAME"]
LOG_LEVEL = os.environ["LOG_LEVEL"]
TOKEN_DURATION = int(os.environ["TOKEN_DURATION"])
SHARED_SERVER_URL = os.environ.get('SS_URL','https://taller2-fiuber-shared-server.herokuapp.com/api/')
SS_TOKEN = requests.post(urljoin(SHARED_SERVER_URL, 'auth/token'), json={'username': "appserver",
                                                                         'password': "appserver"}).json()['token']


def get_log_level(log_level):
    if log_level == "INFO":
        return logging.INFO
    elif log_level == "DEBUG":
        return logging.DEBUG
    elif log_level == "WARN":
        return logging.WARN
    elif log_level == "ERROR":
        return logging.ERROR
    return logging.info


@application.route("/")
def index():
    return "Hello world!"


@application.route("/api/post", methods=['GET'])
def api_post():
    data = list()
    data.append({"message": "Buenas buenas, la app se comunica con el server."})
    return jsonify(data)


@application.route("/test/users")
def get_db_users():
    client = MongoClient(DB_URL)
    users = client.fiuberdb.users.find({}, {"name": 1, "_id": 0})
    data = []
    while users.alive:
        data.append(users.next()["name"])
    return jsonify(data)


@application.route("/test/log")
def log_test():

    application.logger.warning('Log test (%d st line)', 1)
    application.logger.error('No error occurred,just testing')
    application.logger.info('Info test')
    application.logger.debug('debut info')
    return "Done"


formatter = logging.Formatter(
    "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
handler = StreamHandler(sys.stdout)
handler.setLevel(get_log_level(LOG_LEVEL))
handler.setFormatter(formatter)
application.logger.addHandler(handler)
application.logger.setLevel(get_log_level(LOG_LEVEL))

db = MongoClient(DB_URL)[DB_NAME]
from src.handlers.RegisterHandler import REGISTRATION_BLUEPRINT
from src.handlers.SecurityHandler import SECURITY_BLUEPRINT
from src.handlers.DriversHandler import DRIVERS_BLUEPRINT
from src.handlers.PositionHandler import POSITION_BLUEPRINT
from src.handlers.RiderHandler import RIDERS_BLUEPRINT
from src.handlers.TokenRegistrationHandler import TOKEN_MANIPULATION_BLUEPRINT
application.register_blueprint(REGISTRATION_BLUEPRINT)
application.register_blueprint(SECURITY_BLUEPRINT)
application.register_blueprint(DRIVERS_BLUEPRINT)
application.register_blueprint(POSITION_BLUEPRINT)
application.register_blueprint(RIDERS_BLUEPRINT)
application.register_blueprint(TOKEN_MANIPULATION_BLUEPRINT)

if __name__ == "__main__":

    application.run(debug=True, host='0.0.0.0')
