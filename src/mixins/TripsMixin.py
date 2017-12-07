from src.models import User


def add_usernames_to_trip(trip):
    if trip['driver_id']:
        trip['driver_username'] = User.get_user_by_uid(trip['driver_id']).username
    if trip['passenger_id']:
        trip['passenger_username'] = User.get_user_by_uid(trip['passenger_id']).username
    return trip