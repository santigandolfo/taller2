"""Backoffice website"""

from flask import Blueprint, request, render_template, redirect,\
    url_for, session, flash
from flask_googlemaps import GoogleMaps
from app import ADMIN_USER, ADMIN_PWD, application, db
from src.services.google_maps import GOOGLE_KEY
from src.services.push_notifications import send_message_to_multiple_users
from src.mixins.DriversMixin import DriversMixin

WEBSITE_BLUEPRINT = Blueprint('website', __name__, url_prefix="/website")


mocked_positions = [
        {
            'username': 'lucas',
            'longitude': -58.3962300,
            'latitude': -34.6031510
        }, {
            'username': 'finn',
            'longitude': -58.3752300,
            'latitude': -34.6131510
        }, {
            'username': 'will',
            'longitude': -58.3872300,
            'latitude': -34.6221510
        }, {
            'username': 'mike',
            'longitude': -58.3672300,
            'latitude': -34.6341510
        }
    ]

mocked_drivers = ['lucas', 'finn']


@WEBSITE_BLUEPRINT.route("/login", methods=["GET", "POST"])
def login():
    """Login template/login form submitter"""
    if request.method == 'POST':
        data = request.form
        user = data.get("user", "")
        pwd = data.get("password", "")
        if user == ADMIN_USER and pwd == ADMIN_PWD:
            session['admin'] = True
            return redirect(url_for("website.index"))
    return render_template("login.html")


@WEBSITE_BLUEPRINT.route("/logout")
def logout():
    """Logout from the website"""
    flash('You were logged out')
    session['admin'] = False
    return redirect(url_for("website.index"))


@WEBSITE_BLUEPRINT.route("/available-drivers")
def available_drivers():
    """Show available_drivers position"""
    if not session.get('admin', False):
        return redirect(url_for('website.login'))
    try:
        GoogleMaps(application, key=GOOGLE_KEY)
    except:
        pass

    drivers_with_positions = DriversMixin.get_positions(DriversMixin.get_available_drivers())

    drivers_with_positions = []
    for position in mocked_positions:
        if position['username'] in mocked_drivers:
            drivers_with_positions.append(position)

    positions = [(driver['latitude'], driver['longitude'])
                 for driver in drivers_with_positions]

    print "hola"
    return render_template("map-page.html", markers=positions, title="Available drivers' positions")


@WEBSITE_BLUEPRINT.route("/users")
def users():
    """Home for backoffice website"""
    if not session.get('admin', False):
        return redirect(url_for('website.login'))

    if not session.get('admin', False):
        return redirect(url_for('website.login'))
    try:
        GoogleMaps(application, key=GOOGLE_KEY)
    except:
        pass

    drivers_username = db.drivers.find({}, {'username': 1, '_id': 0})

    drivers_username_list = [driver_name for driver_name in drivers_username]

    drivers_username_list = mocked_drivers
    positions = db.positions.find()

    positions = mocked_positions

    markers = []
    for position in positions:
        if position['username'] in drivers_username_list:
            icon = '/static/fiuber-marker.png'
        else:
            icon = '/static/person-marker.png'
        dict_to_be_addded = {'lat': position['latitude'],
                             'lng': position['longitude'],
                             'icon': icon}
        markers.append(dict_to_be_addded)

    print markers
    print "hola"
    return render_template("map-page.html", markers=markers, title="Users' positions")


@WEBSITE_BLUEPRINT.route("/send-notifications", methods=["GET", "POST"])
def send_notifications():
    """Home for backoffice website"""
    if request.method == 'POST':
        list_of_tokens = list(db.users.find({}, {'push_token': 1, '_id': 0}))
        data = request.form
        send_message_to_multiple_users(data.get("title", "FIUBER"),
                                       data.get("message", "Hello!"),
                                       list_of_tokens)
    return render_template('send-notifications.html')


@WEBSITE_BLUEPRINT.route("")
def index():
    """Home for backoffice website"""
    if not session.get('admin', False):
        return redirect(url_for('website.login'))
    return render_template('home.html')

