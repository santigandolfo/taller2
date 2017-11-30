from src.mixins.DriversMixin import DriversMixin


MAX_DISTANCE = 0.1

class TrackingTripsMixin(object):
    """Utility class for anything related with tracking trips"""

    @staticmethod
    def check_positions_with_location(usernames,location):
        """Checks if all the users specified in usernames are near enough the desired location"""
        positions = DriversMixin.get_positions(usernames)
        for position in positions:
            if DriversMixin.distance((position['latitude'],position['longitude']),location) > MAX_DISTANCE:
                return False
        return True
