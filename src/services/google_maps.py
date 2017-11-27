import requests
import os

GOOGLE_KEY = os.environ["GOOGLE_KEY"]


def get_directions(data):
    parameters = {
        "origin": str(data[u'latitude_initial']) + ", " + str(data[u'longitude_initial']),
        "destination": str(data[u'latitude_final']) + ", " + str(data[u'longitude_final']),
        "key": GOOGLE_KEY
    }
    return requests.get("https://maps.googleapis.com/maps/api/directions/json", params=parameters)