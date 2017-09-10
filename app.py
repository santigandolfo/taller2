from flask import Flask,jsonify
from src.controllers import AppController
from pymongo import MongoClient
import os
import logging
from logging import StreamHandler
import sys


application = Flask(__name__)


DB_URL = os.environ["DB_URL"]

@application.route("/")
def index():
    return AppController.index()

@application.route("/api/post", methods=['GET'])
def api_post():
    data = []    
    data.append( { "message":"Buenas buenas, la app se comunica con el server."} )
    return jsonify(data)

@application.route("/test/users")
def get_db_users():
    client = MongoClient(DB_URL)
    users = client.fiuberdb.users.find({},{"name": 1, "_id":0})
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


@application.before_first_request
def initialize_log():
    formatter = logging.Formatter(
        "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
    handler = StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    application.logger.addHandler(handler)
    application.logger.setLevel(logging.DEBUG)


if __name__ == "__main__":
    
    application.run(debug=True, host='0.0.0.0')



