# coding: utf8

import unittest
import json
import time
from tests.base import BaseTestCase
from mock import patch, Mock
from app import TOKEN_DURATION
directions_return_example = {
    "geocoded_waypoints": [
        {
            "geocoder_status": "OK",
            "place_id": "EilBcmNvcyAyMDEyLTIwMzAsIEMxNDI4QUZGIENBQkEsIEFyZ2VudGluYQ",
            "types": ["street_address"]
        },
        {
            "geocoder_status": "OK",
            "place_id": "EjFBdi4gUGFzZW8gQ29sw7NuIDgyOC04MzAsIEJ1ZW5vcyBBaXJlcywgQXJnZW50aW5h",
            "types": ["street_address"]
        }
    ],
    "routes": [
        {
            "bounds": {
                "northeast": {
                    "lat": -34.5584317,
                    "lng": -58.3669878
                },
                "southwest": {
                    "lat": -34.618374,
                    "lng": -58.4538325
                }
            },
            "copyrights": "Map data ©2017 Google",
            "legs": [
                {
                    "distance": {
                        "text": "12.3 km",
                        "value": 12251
                    },
                    "duration": {
                        "text": "32 mins",
                        "value": 1926
                    },
                    "end_address": "Av. Paseo Colon 828-830, Buenos Aires, Argentina",
                    "end_location": {
                        "lat": -34.6176331,
                        "lng": -58.3684494
                    },
                    "start_address": "Arcos 2012-2030, C1428AFF CABA, Argentina",
                    "start_location": {
                        "lat": -34.5610035,
                        "lng": -58.4532958
                    },
                    "steps": [
                        {
                            "distance": {
                                "text": "81 m",
                                "value": 81
                            },
                            "duration": {
                                "text": "1 min",
                                "value": 24
                            },
                            "end_location": {
                                "lat": -34.560421,
                                "lng": -58.4538325
                            },
                            "html_instructions": "Head \u003cb\u003enorthwest\u003c/b\u003e "
                                                 "on \u003cb\u003eArcos\u003c/b\u003e toward "
                                                 "\u003cb\u003eAv. Juramento\u003c/b\u003e",
                            "polyline": {
                                "points": "fe}qEbtwcJsBhB"
                            },
                            "start_location": {
                                "lat": -34.5610035,
                                "lng": -58.4532958
                            },
                            "travel_mode": "DRIVING"
                        }
                    ],
                    "traffic_speed_entry": [],
                    "via_waypoint": []
                }
            ],
            "overview_polyline": {
                "points": "fe}qEbtwcJsBhBmBsD}BkEcBkDc@cAYa@jC{E`@}@jBwDl@wBh@yBHQNa@r@_B|@eBZi@d@kAfBmFXuA^qB^qBd@{Cl@_GDu@L}BCQKc@V{BL}@\\aBZmAt@qBxGwMbC{E|BwE~AoCd@a@jAsBz@cB|BeFbAqB|@qBNWXs@|AaDTe@hCiFhAcCt@yB`AqD~BiHfBmFn@kBhAeDvB{Fv@aCpBaFvA}BLYBAFCNMRa@D]CUAI`@iBHi@?[zA_FrAoEhA{CXs@x@qCxBiGbAgD|BeFfAaBxA}An@{@lCqDrCaEp@sAt@gCTqA^}B|B{IPoAz@yIZwCb@yBn@iCrAqGrA_H\\yAdAkEXeEGcABs@Jq@XuAJa@Ja@bAiCxBaGp@aB^eA@MhAgCtFuLr@cCb@}@jBmEtA{CdAaC`AeBpAwBpEgIpBwCRAHEj@qAbBiDbAqCWQkDoCsAeAe@m@e@g@GMEMhA_@|LsDbHwBfNgEtEwAlH}BZKtBObNs@bOw@~Lu@rLq@vDSxAGfEWNfDRxFDpAlFEnEEvCBfE@v@Ap@Kt@SAYMiBAYOAKEIGY?aAD"
            },
            "summary": "Av. del Libertador",
            "warnings": [],
            "waypoint_order": []
        }
    ],
    "status": "OK"
}


mock_direction = Mock()
mock_direction.ok = True
mock_direction.status_code = 200
mock_direction.json = Mock()
mock_direction.json.return_value = dict(directions_return_example)


class TestRequestsSubmission(BaseTestCase):
    @patch('requests.get', return_value=mock_direction)
    @patch('requests.post')
    def test_simple_request_submission_driver_assigned(self, mock_post, mocked_google_response):
        """ Test case for a simple request succesfully submitted"""
        mock_post.return_value = Mock()
        mock_post.return_value.json.return_value = {'id': "1"}
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 201
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(dict(
                    username='juan',
                    password='123456',
                    type='driver'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            auth_token = data['auth_token']
            response = self.client.patch(
                '/drivers/juan',
                data=json.dumps(dict(
                    duty=True
                )),
                headers=dict(
                    Authorization='Bearer ' + auth_token
                ),
                content_type='application/json'
            )
            response = self.client.put(
                '/users/juan/coordinates',
                headers=dict(
                    Authorization='Bearer ' + auth_token
                ),
                data=json.dumps(dict(
                    latitude='30.12',
                    longitude='41.00'
                )),
                content_type='application/json'
            )
            response = self.client.post(
                '/users',
                data=json.dumps(dict(
                    username='pedro',
                    password='123456',
                    type='passenger'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            auth_token = data['auth_token']
            mock_post.return_value = Mock()
            mock_post.return_value.json.return_value = {'value': 25}
            mock_post.return_value.ok = True
            mock_post.return_value.status_code = 200
            response = self.client.post(
                '/riders/pedro/request',
                data=json.dumps(dict(
                    latitude_initial=30.00,
                    latitude_final=31.32,
                    longitude_initial=42,
                    longitude_final=43.21
                )),
                headers=dict(
                    Authorization='Bearer ' + auth_token
                ),
                content_type='application/json'
            )

            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'request_submitted')
            self.assertEqual(data['status'], 'success')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 201)

    @patch('requests.get', return_value=mock_direction)
    @patch('requests.post')
    def test_request_submission_with_validation_transform_no_driver_available(self, mock_post, mocked_google_response):
        """ Test case for a request where data has to be transformed during validation"""
        mock_post.return_value = Mock()
        mock_post.return_value.json.return_value = {'id': "1"}
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 201
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(dict(
                    username='pedro',
                    password='123456',
                    type='passenger'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            auth_token = data['auth_token']
            response = self.client.post(
                '/riders/pedro/request',
                data=json.dumps(dict(
                    latitude_initial='30.00',
                    latitude_final='31.32',
                    longitude_initial='42',
                    longitude_final='43.21'
                )),
                headers=dict(
                    Authorization='Bearer ' + auth_token
                ),
                content_type='application/json'
            )

            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'no_driver_available')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 200)

    @patch('requests.get', return_value=mock_direction)
    @patch('requests.post')
    def test_request_submission_missing_parameter(self, mock_post, mocked_google_response):
        """ Test case for a request with no latitude_final"""
        mock_post.return_value = Mock()
        mock_post.return_value.json.return_value = {'id': "1"}
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 201
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(dict(
                    username='pedro',
                    password='123456',
                    type='passenger'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            auth_token = data['auth_token']
            response = self.client.post(
                '/riders/pedro/request',
                data=json.dumps(dict(
                    latitude_initial=30.00,
                    longitude_initial=42,
                    longitude_final=43.21
                )),
                headers=dict(
                    Authorization='Bearer ' + auth_token
                ),
                content_type='application/json'
            )

            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'bad_request_data')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 400)

    @patch('requests.get', return_value=mock_direction)
    @patch('requests.post')
    def test_request_submission_wrong_parameter(self, mock_post, mocked_google_response):
        """ Test case for a request with a not transformable string parameter"""
        mock_post.return_value = Mock()
        mock_post.return_value.json.return_value = {'id': "1"}
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 201
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(dict(
                    username='pedro',
                    password='123456',
                    type='passenger'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            auth_token = data['auth_token']
            response = self.client.post(
                '/riders/pedro/request',
                data=json.dumps(dict(
                    latitude_initial="Argentina",
                    latitude_final=31.32,
                    longitude_initial=42,
                    longitude_final=43.21
                )),
                headers=dict(
                    Authorization='Bearer ' + auth_token
                ),
                content_type='application/json'
            )

            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'bad_request_data')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 400)

    @patch('requests.get', return_value=mock_direction)
    @patch('requests.post')
    def test_request_submission_driver(self, mock_post, mocked_google_response):
        """ Test case for a request submitted for a driver"""
        mock_post.return_value = Mock()
        mock_post.return_value.json.return_value = {'id': "1"}
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 201
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(dict(
                    username='pedro',
                    password='123456',
                    type='driver'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            auth_token = data['auth_token']
            response = self.client.post(
                '/riders/pedro/request',
                data=json.dumps(dict(
                    latitude_initial=30.00,
                    latitude_final=31.32,
                    longitude_initial=42,
                    longitude_final=43.21
                )),
                headers=dict(
                    Authorization='Bearer ' + auth_token
                ),
                content_type='application/json'
            )

            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'rider_not_found')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 404)

    @patch('requests.get', return_value=mock_direction)
    @patch('requests.post')
    def test_request_submission_unauthorized(self, mock_post, mocked_google_response):
        """ Test case for a request submitted by an unauthorized user"""
        mock_post.return_value = Mock()
        mock_post.return_value.json.return_value = {'id': "1"}
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 201
        with self.client:
            self.client.post(
                '/users',
                data=json.dumps(dict(
                    username='pedro',
                    password='123456',
                    type='passenger'
                )),
                content_type='application/json'
            )
            response = self.client.post(
                '/users',
                data=json.dumps(dict(
                    username='javier',
                    password='123456',
                    type='driver'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            auth_token = data['auth_token']
            response = self.client.post(
                '/riders/pedro/request',
                data=json.dumps(dict(
                    latitude_initial=30.00,
                    latitude_final=31.32,
                    longitude_initial=42,
                    longitude_final=43.21
                )),
                headers=dict(
                    Authorization='Bearer ' + auth_token
                ),
                content_type='application/json'
            )

            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'unauthorized_request')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 401)

    @patch('requests.get', return_value=mock_direction)
    @patch('requests.post')
    def test_request_submission_missing_token(self, mock_post, mocked_google_response):
        """ Test case for a request submitted without a token"""
        mock_post.return_value = Mock()
        mock_post.return_value.json.return_value = {'id': "1"}
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 201
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(dict(
                    username='pedro',
                    password='123456',
                    type='passenger'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            response = self.client.post(
                '/riders/pedro/request',
                data=json.dumps(dict(
                    latitude_initial=30.00,
                    latitude_final=31.32,
                    longitude_initial=42,
                    longitude_final=43.21
                )),
                content_type='application/json'
            )

            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'missing_token')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 401)

    @patch('requests.get', return_value=mock_direction)
    @patch('requests.post')
    def test_request_submission_invalid_token(self, mock_post, mocked_google_response):
        """ Test case for a request submitted with an invalid token"""
        mock_post.return_value = Mock()
        mock_post.return_value.json.return_value = {'id': "1"}
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 201
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(dict(
                    username='pedro',
                    password='123456',
                    type='passenger'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            response = self.client.post(
                '/riders/pedro/request',
                data=json.dumps(dict(
                    latitude_initial=30.00,
                    latitude_final=31.32,
                    longitude_initial=42,
                    longitude_final=43.21
                )),
                headers=dict(
                    Authorization='Bearer asjdhasheo2q3ejjae'
                ),
                content_type='application/json'
            )

            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'invalid_token')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 401)

    @patch('requests.get', return_value=mock_direction)
    @patch('requests.post')
    def test_request_submission_expired_token(self, mock_post, mocked_google_response):
        """ Test case for a request submitted with an expired token"""
        mock_post.return_value = Mock()
        mock_post.return_value.json.return_value = {'id': "1"}
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 201
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(dict(
                    username='pedro',
                    password='123456',
                    type='passenger'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            auth_token = data['auth_token']
            time.sleep(TOKEN_DURATION + 1)
            response = self.client.post(
                '/riders/pedro/request',
                data=json.dumps(dict(
                    latitude_initial=30.00,
                    latitude_final=31.32,
                    longitude_initial=42,
                    longitude_final=43.21
                )),
                headers=dict(
                    Authorization='Bearer ' + auth_token
                ),
                content_type='application/json'
            )

            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'expired_token')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 401)





if __name__ == '__main__':
    unittest.main()
