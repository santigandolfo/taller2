from src.mixins.DriversMixin import DriversMixin
from app import application

MAX_DISTANCE = 0.1

class TrackingTripsMixin(object):
    """Utility class for anything related with tracking trips"""

    @staticmethod
    def check_positions_with_location(usernames,location):
        """Checks if all the users specified in usernames are near enough the desired location"""
        positions = DriversMixin.get_positions(usernames)
        if positions.count() < len(usernames):
            application.logger.info("There is an unknown position")
            return False
        for position in positions:
            distance = DriversMixin.distance((position['latitude'],position['longitude']),location)
            application.logger.info("Distance between user and location is: {}".format(distance))
            if  distance > MAX_DISTANCE:
                return False
        return True
