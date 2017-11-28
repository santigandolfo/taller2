"""Mixins for drivers stuff"""
import math
from functools import reduce
from app import db


class DriversMixin(object):
    """Utility class for anything related with drivers"""

    @staticmethod
    def get_available_drivers():
        """Gets the ids of all the available drivers"""

        return [driver['username'] for driver in
                db.drivers.find({"available": True}, {'username': 1, '_id': 0})]

    @staticmethod
    def get_positions(drivers_names):
        return db.positions.find({'username': {'$in': drivers_names}},
                                 {'username': 1, 'latitude': 1, 'longitude': 1, '_id': 0})

    @staticmethod
    def distance(origin, destination):
        lat1, lon1 = origin
        lat2, lon2 = destination
        radius = 6371  # km

        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) \
                                                      * math.cos(math.radians(lat2)) \
                                                      * math.sin(dlon / 2) * math.sin(
            dlon / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        d = radius * c

        return d

    @staticmethod
    def get_closer_driver(location):
        """Get the id of the driver which is closer to the given location"""
        drivers_names = list(DriversMixin.get_available_drivers())
        drivers_with_position = DriversMixin.get_positions(drivers_names)
        drivers_with_distance = [(driver['username'],
                                  DriversMixin.distance((driver['latitude'], driver['longitude']), location))
                                 for driver in drivers_with_position]

        driver = reduce(lambda x, y: x if x[1] < y[1] else y, drivers_with_distance, (None, float("inf")))
        return driver[0]
