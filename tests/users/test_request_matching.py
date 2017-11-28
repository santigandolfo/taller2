import unittest
import json
from tests.base import BaseTestCase
from mock import patch, Mock
from src.mixins.DriversMixin import DriversMixin
from app import db


class TestRequestMatching(BaseTestCase):

    def test_gets_available_drivers(self):
        drivers = [{'username': 'x' * x, 'available': x % 2 == 0} for x in range(1, 5)]
        db.drivers.insert_many(drivers)
        available_drivers = list(DriversMixin.get_available_drivers())
        self.assertEqual(len(available_drivers), 2)
        self.assertTrue('xx' in available_drivers)
        self.assertTrue('xxxx' in available_drivers)

    def test_get_none_drivers_if_there_isnt_any_available(self):
        drivers = [{'username': 'x'*x, 'available': False} for x in range(1, 5)]
        db.drivers.insert_many(drivers)
        available_drivers = list(DriversMixin.get_available_drivers())
        self.assertEqual(len(available_drivers), 0)

    def test_get_correct_positions(self):
        positions = [{'username': 'x'*x, 'latitude': x+45, 'longitude': 2*x+40}
                    for x in range(1, 5)]
        usernames = ['x', 'xxxx']
        db.positions.insert_many(positions)
        drivers_position = list(DriversMixin.get_positions(usernames))
        self.assertEqual(len(drivers_position), 2)
        self.assertTrue({'username': 'x', 'latitude': 46, 'longitude': 42}
                        in drivers_position)
        self.assertTrue({'username': 'xxxx', 'latitude': 49, 'longitude': 48}
                        in drivers_position)

    def test_get_correct_positions_without_usernames_returns_empty_list(self):
        positions = [{'username': 'x' * x, 'latitude': x + 45, 'longitude': 2 * x + 40}
                     for x in range(1, 5)]
        usernames = []
        db.positions.insert_many(positions)
        drivers_position = list(DriversMixin.get_positions(usernames))
        self.assertEqual(len(drivers_position), 0)

    def test_calculate_right_distance(self):

        latitude_initial = 40.654
        longitude_initial = -35
        latitude_final = 40.654
        longitude_final = -36

        distance = DriversMixin.distance((latitude_initial,longitude_initial),(latitude_final,longitude_final))
        self.assertAlmostEquals(distance, 84.36, delta=0.01)

    def test_calculate_zero_distance_on_equal_position(self):

        latitude_initial = 40.654
        longitude_initial = -35

        distance = DriversMixin.distance((latitude_initial, longitude_initial), (latitude_initial,longitude_initial))
        self.assertAlmostEquals(distance, 0, delta=0.0001)


    def test_get_closest_driver(self):
        drivers = [{'username': 'x' * x, 'available': x % 2 == 0} for x in range(1, 5)]
        db.drivers.insert_many(drivers)
        positions = [{'username': 'x' * x, 'latitude': x + 45, 'longitude': 2 * x + 40}
                     for x in range(1, 5)]
        db.positions.insert_many(positions)
        latitude = 47
        longitude = 45
        closer_driver = DriversMixin.get_closer_driver((latitude, longitude))
        self.assertEqual(closer_driver, 'xx')

    def test_get_closest_driver_only_one_available(self):
        drivers = [{'username': 'x' * x, 'available': x % 4 == 0} for x in range(1, 5)]
        db.drivers.insert_many(drivers)
        positions = [{'username': 'x' * x, 'latitude': x + 45, 'longitude': 2 * x + 40}
                     for x in range(1, 5)]
        db.positions.insert_many(positions)
        latitude = 47
        longitude = 45
        closer_driver = DriversMixin.get_closer_driver((latitude, longitude))
        self.assertEqual(closer_driver, 'xxxx')

    def test_get_closest_driver_only_zero_available(self):
        drivers = [{'username': 'x' * x, 'available': False} for x in range(1, 5)]
        db.drivers.insert_many(drivers)
        positions = [{'username': 'x' * x, 'latitude': x + 45, 'longitude': 2 * x + 40}
                     for x in range(1, 5)]
        db.positions.insert_many(positions)
        latitude = 47
        longitude = 45
        closer_driver = DriversMixin.get_closer_driver((latitude, longitude))
        self.assertIs(closer_driver, None)
