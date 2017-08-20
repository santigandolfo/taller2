from flask import Flask
from src.controllers import AppController

application = Flask(__name__)

@application.route("/")
def index():
    return AppController.index()

if __name__ == "__main__":
    application.run(debug=True, host='0.0.0.0')