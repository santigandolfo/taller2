import json
from tests.base import BaseTestCase
from mock import patch, Mock


class TestRequestMatching(BaseTestCase):
    users = {}

    def complete_register(self, name, type, latitude, longitude):
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(dict(
                    username=name,
                    password='123456',
                    type=type
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            auth_token = data['auth_token']

            self.client.put(
                '/users/{}/coordinates'.format(name),
                data=json.dumps(dict(
                    latitude=latitude,
                    longitude=longitude
                )),
                headers=dict(
                    Authorization='Bearer ' + auth_token
                ),
                content_type='application/json'
            )

            return auth_token

    def make_available(self, name, token):
        self.client.patch(
            '/drivers/{}'.format(name),
            data=json.dumps(dict(
                duty=True
            )),
            headers=dict(
                Authorization='Bearer ' + token
            ),
            content_type='application/json'
        )

    def setUp(self):
        BaseTestCase.setUp(self)
        with patch('requests.post') as mock_post:
            mock_post.return_value = Mock()
            mock_post.return_value.ok = True
            mock_post.return_value.status_code = 201

            mock_post.return_value.json.return_value = {'id': "1"}
            self.users['joe_smith'] = {}
            self.users['joe_smith']['token'] =\
                self.complete_register('joe_smith', 'rider', 30, 40)

            mock_post.return_value.json.return_value = {'id': "2"}
            self.users['william_dafoe'] = {}
            self.users['william_dafoe']['token'] =\
                self.complete_register('william_dafoe', 'rider', 50, 60)

            mock_post.return_value.json.return_value = {'id': "3"}
            self.users['johny'] = {}
            self.users['johny']['token'] = self.complete_register('johny', 'driver', 31, 41)
            self.make_available('johny', self.users['johny']['token'])

            mock_post.return_value.json.return_value = {'id': "4"}
            self.users['el_transportador'] = {}
            self.users['el_transportador']['token'] =\
                self.complete_register('el_transportador', 'driver', 25, 35)
            self.make_available('el_transportador', self.users['el_transportador']['token'])

            mock_post.return_value.json.return_value = {'id': "5"}
            self.users['billy'] = {}
            self.users['billy']['token'] = \
                self.complete_register('billy', 'rider', 50, 60)

    def test_two_trips_assigned_correctly_one_missing_driver(self):
        with self.client:
            with patch('src.handlers.RequestHandler.get_directions') as mock_directions:

                mock_directions.return_value = Mock()
                mock_directions.return_value.ok = True
                mock_directions.return_value.json.return_value = {
                    'routes': [
                        {
                            'overview_polyline': {
                                'points': "fe}qEbtwcJsBhBmBsD}BkEcBkDc@cAYa@jC{E`@}@"
                                          "jBwDl@wBh@yBHQNa@r@_B|@eBZi@d@kAfBmFXuA^q"
                                          "B^qBd@{Cl@_GDu@L}BCQKc@V{BL}@\\aBZmAt@qBx"
                                          "GwMbC{E|BwE~A"
                            },
                            'legs': [
                                {
                                    'distance': {
                                        'value': 5
                                    }
                                }
                            ]

                        }
                    ]
                }
                response = self.client.post(
                    '/riders/joe_smith/request',
                    data=json.dumps(dict(
                        latitude_initial=30.00,
                        latitude_final=40,
                        longitude_initial=50,
                        longitude_final=60
                    )),
                    headers=dict(
                        Authorization='Bearer ' + self.users['joe_smith']['token']
                    ),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                self.assertEqual(data['message'], 'request_submitted')
                self.assertEqual(data['status'], 'success')
                self.assertEqual(response.content_type, 'application/json')
                self.assertEqual(response.status_code, 201)
                self.assertEqual(data['driver'], 'johny')

                response = self.client.post(
                    '/riders/william_dafoe/request',
                    data=json.dumps(dict(
                        latitude_initial=30.00,
                        latitude_final=40,
                        longitude_initial=50,
                        longitude_final=60
                    )),
                    headers=dict(
                        Authorization='Bearer ' + self.users['william_dafoe']['token']
                    ),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                self.assertEqual(data['message'], 'request_submitted')
                self.assertEqual(data['status'], 'success')
                self.assertEqual(response.content_type, 'application/json')
                self.assertEqual(response.status_code, 201)
                self.assertEqual(data['driver'], 'el_transportador')

                response = self.client.post(
                    '/riders/billy/request',
                    data=json.dumps(dict(
                        latitude_initial=30.00,
                        latitude_final=40,
                        longitude_initial=50,
                        longitude_final=60
                    )),
                    headers=dict(
                        Authorization='Bearer ' + self.users['billy']['token']
                    ),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                self.assertEqual(data['message'], 'no_driver_available')
                self.assertEqual(data['status'], 'fail')
                self.assertEqual(response.content_type, 'application/json')
                self.assertEqual(response.status_code, 200)
                self.assertTrue('driver' not in data)

    def test_driver_assigned_two_times(self):
        """One driver is assigned to a trip, the trip is cancelled, that driver is assigned again"""
        with self.client:
            with patch('src.handlers.RequestHandler.get_directions') as mock_directions:

                mock_directions.return_value = Mock()
                mock_directions.return_value.ok = True
                mock_directions.return_value.json.return_value = {
                    'routes': [
                        {
                            'overview_polyline': {
                                'points': "fe}qEbtwcJsBhBmBsD}BkEcBkDc@cAYa@jC{E`@}@"
                                          "jBwDl@wBh@yBHQNa@r@_B|@eBZi@d@kAfBmFXuA^q"
                                          "B^qBd@{Cl@_GDu@L}BCQKc@V{BL}@\\aBZmAt@qBx"
                                          "GwMbC{E|BwE~A"
                            },
                            'legs': [
                                {
                                    'distance': {
                                        'value': 5
                                    }
                                }
                            ]

                        }
                    ]
                }
                response = self.client.post(
                    '/riders/joe_smith/request',
                    data=json.dumps(dict(
                        latitude_initial=30.00,
                        latitude_final=40,
                        longitude_initial=50,
                        longitude_final=60
                    )),
                    headers=dict(
                        Authorization='Bearer ' + self.users['joe_smith']['token']
                    ),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                self.assertEqual(data['message'], 'request_submitted')
                self.assertEqual(data['status'], 'success')
                self.assertEqual(response.content_type, 'application/json')
                self.assertEqual(response.status_code, 201)
                self.assertEqual(data['driver'], 'johny')

                response = self.client.delete(
                    '/requests/{}'.format(data['id']),
                    headers=dict(
                        Authorization='Bearer ' + self.users['joe_smith']['token']
                    ),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                self.assertEqual(data['message'], 'request_cancelled')

                self.assertEqual(data['status'], 'success')
                self.assertEqual(response.content_type, 'application/json')
                self.assertEqual(response.status_code, 203)

                response = self.client.post(
                    '/riders/william_dafoe/request',
                    data=json.dumps(dict(
                        latitude_initial=30.00,
                        latitude_final=40,
                        longitude_initial=50,
                        longitude_final=60
                    )),
                    headers=dict(
                        Authorization='Bearer ' + self.users['william_dafoe']['token']
                    ),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                self.assertEqual(data['message'], 'request_submitted')
                self.assertEqual(data['status'], 'success')
                self.assertEqual(response.content_type, 'application/json')
                self.assertEqual(response.status_code, 201)
                self.assertEqual(data['driver'], 'johny')

    def test_driver_assigned_two_times(self):
        """One driver is assigned to a trip, the trip is cancelled, that driver is assigned again"""
        with self.client:
            with patch('src.handlers.RequestHandler.get_directions') as mock_directions:

                mock_directions.return_value = Mock()
                mock_directions.return_value.ok = True
                mock_directions.return_value.json.return_value = {
                    'routes': [
                        {
                            'overview_polyline': {
                                'points': "fe}qEbtwcJsBhBmBsD}BkEcBkDc@cAYa@jC{E`@}@"
                                          "jBwDl@wBh@yBHQNa@r@_B|@eBZi@d@kAfBmFXuA^q"
                                          "B^qBd@{Cl@_GDu@L}BCQKc@V{BL}@\\aBZmAt@qBx"
                                          "GwMbC{E|BwE~A"
                            },
                            'legs': [
                                {
                                    'distance': {
                                        'value': 5
                                    }
                                }
                            ]

                        }
                    ]
                }
                response = self.client.post(
                    '/riders/joe_smith/request',
                    data=json.dumps(dict(
                        latitude_initial=30.00,
                        latitude_final=40,
                        longitude_initial=50,
                        longitude_final=60
                    )),
                    headers=dict(
                        Authorization='Bearer ' + self.users['joe_smith']['token']
                    ),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                self.assertEqual(data['message'], 'request_submitted')
                self.assertEqual(data['status'], 'success')
                self.assertEqual(response.content_type, 'application/json')
                self.assertEqual(response.status_code, 201)
                self.assertEqual(data['driver'], 'johny')

                response = self.client.delete(
                    '/requests/{}'.format(data['id']),
                    headers=dict(
                        Authorization='Bearer ' + self.users['joe_smith']['token']
                    ),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                self.assertEqual(data['message'], 'request_cancelled')

                self.assertEqual(data['status'], 'success')
                self.assertEqual(response.content_type, 'application/json')
                self.assertEqual(response.status_code, 203)

                response = self.client.post(
                    '/riders/william_dafoe/request',
                    data=json.dumps(dict(
                        latitude_initial=30.00,
                        latitude_final=40,
                        longitude_initial=50,
                        longitude_final=60
                    )),
                    headers=dict(
                        Authorization='Bearer ' + self.users['william_dafoe']['token']
                    ),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                self.assertEqual(data['message'], 'request_submitted')
                self.assertEqual(data['status'], 'success')
                self.assertEqual(response.content_type, 'application/json')
                self.assertEqual(response.status_code, 201)
                self.assertEqual(data['driver'], 'johny')

    def test_driver_assigned_two_times_in_succesful_trips(self):
        """One driver is assigned to a trip, the trip is closed, that driver is assigned again,
        the trip is closed, the driver is available again"""
        with self.client:
            with patch('src.handlers.RequestHandler.get_directions') as mock_directions:

                mock_directions.return_value = Mock()
                mock_directions.return_value.ok = True
                mock_directions.return_value.json.return_value = {
                    'routes': [
                        {
                            'overview_polyline': {
                                'points': "fe}qEbtwcJsBhBmBsD}BkEcBkDc@cAYa@jC{E`@}@"
                                          "jBwDl@wBh@yBHQNa@r@_B|@eBZi@d@kAfBmFXuA^q"
                                          "B^qBd@{Cl@_GDu@L}BCQKc@V{BL}@\\aBZmAt@qBx"
                                          "GwMbC{E|BwE~A"
                            },
                            'legs': [
                                {
                                    'distance': {
                                        'value': 5
                                    }
                                }
                            ]

                        }
                    ]
                }
                response = self.client.post(
                    '/riders/joe_smith/request',
                    data=json.dumps(dict(
                        latitude_initial=30.00,
                        latitude_final=40,
                        longitude_initial=50,
                        longitude_final=60
                    )),
                    headers=dict(
                        Authorization='Bearer ' + self.users['joe_smith']['token']
                    ),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                self.assertEqual(data['message'], 'request_submitted')
                self.assertEqual(data['status'], 'success')
                self.assertEqual(response.content_type, 'application/json')
                self.assertEqual(response.status_code, 201)
                self.assertEqual(data['driver'], 'johny')

                with patch('requests.post') as mock_post:
                    mock_post.return_value = Mock()
                    mock_post.return_value.json.return_value = {'id': "1"}
                    mock_post.return_value.ok = True
                    mock_post.return_value.status_code = 201
                    response = self.client.delete(
                        '/drivers/johny/trip',
                        headers=dict(
                            Authorization='Bearer ' + self.users['johny']['token']
                        ),
                        content_type='application/json'
                    )
                    data = json.loads(response.data.decode())
                    self.assertEqual(data['message'], 'trip_finished')
                    self.assertEqual(data['status'], 'success')
                    self.assertEqual(response.content_type, 'application/json')
                    self.assertEqual(response.status_code, 203)

                    mock_post.assert_called_once()

                response = self.client.post(
                    '/riders/william_dafoe/request',
                    data=json.dumps(dict(
                        latitude_initial=30.00,
                        latitude_final=40,
                        longitude_initial=50,
                        longitude_final=60
                    )),
                    headers=dict(
                        Authorization='Bearer ' + self.users['william_dafoe']['token']
                    ),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                self.assertEqual(data['message'], 'request_submitted')
                self.assertEqual(data['status'], 'success')
                self.assertEqual(response.content_type, 'application/json')
                self.assertEqual(response.status_code, 201)
                self.assertEqual(data['driver'], 'johny')





