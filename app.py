from flask import Flask,jsonify
from src.controllers import AppController


application = Flask(__name__)

@application.route("/")
def index():
    return AppController.index()

@application.route("/api/post", methods=['GET'])
def api_post():
    data = []    
    data.append( { "message":"Buenas buenas, la app se comunica con el server."} )
    return jsonify(data)



if __name__ == "__main__":
    application.run(debug=True, host='0.0.0.0')
