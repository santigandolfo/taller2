from flask import Flask,jsonify
from src.controllers import AppController
from pymongo import MongoClient
import os
application = Flask(__name__)


DB_USER = os.environ["DB_USER"]
DB_PWD = os.environ["DB_PWD"]
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
    client = MongoClient("mongodb://"+DB_USER+":"+DB_PWD+"@ds131854.mlab.com:31854/fiuberdb")
    users = client.fiuberdb.users.find({},{"name": 1, "_id":0})
    data = []

    while users.alive:
        data.append(users.next()["name"])
    return jsonify(data)

if __name__ == "__main__":
    application.run(debug=True, host='0.0.0.0')
