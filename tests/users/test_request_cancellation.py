import unittest
import json
from tests.base import BaseTestCase
from mock import patch, Mock
from src.mixins.DriversMixin import DriversMixin
from app import db, TOKEN_DURATION
import app


class TestRequestMatching(BaseTestCase):

    rider_joe_auth_token = ''
    rider_will_auth_token = ''
    driver_auth_token = ''
    request_id = 0

    def setUp(self):
        BaseTestCase.setUp(self)
        with self.client:
            with patch('requests.post') as mock_post:
                mock_post.return_value = Mock()
                mock_post.return_value.json.return_value = {'id': "1"}
                mock_post.return_value.ok = True
                mock_post.return_value.status_code = 201
                response = self.client.post(
                    '/users',
                    data=json.dumps(dict(
                        username='joe_smith',
                        password='123456',
                        type='rider'
                    )),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                self.rider_joe_auth_token = data['auth_token']

                mock_post.return_value.json.return_value = {'id': "2"}
                response = self.client.post(
                    '/users',
                    data=json.dumps(dict(
                        username='william_dafoe',
                        password='123456',
                        type='rider'
                    )),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                self.rider_will_auth_token = data['auth_token']

                mock_post.return_value.json.return_value = {'id': "3"}
                response = self.client.post(
                    '/users',
                    data=json.dumps(dict(
                        username='johny',
                        password='123456',
                        type='driver'
                    )),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                self.driver_auth_token = data['auth_token']

                self.client.patch(
                    '/drivers/johny',
                    data=json.dumps(dict(
                        availability=True
                    )),
                    headers=dict(
                        Authorization='Bearer ' + self.driver_auth_token
                    ),
                    content_type='application/json'
                )

                mock_post.return_value.json.return_value = {'id': "4"}
                response = self.client.post(
                    '/users',
                    data=json.dumps(dict(
                        username='johny2',
                        password='123456',
                        type='driver'
                    )),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                self.driver_auth_token = data['auth_token']

                self.client.patch(
                    '/drivers/johny2',
                    data=json.dumps(dict(
                        availability=True
                    )),
                    headers=dict(
                        Authorization='Bearer ' + self.driver_auth_token
                    ),
                    content_type='application/json'
                )

                with patch('src.handlers.RequestHandler.DriversMixin') as mock_mixin:
                    with patch('src.handlers.RequestHandler.get_directions') as mock_directions:

                        mock_mixin.get_closer_driver = Mock()
                        mock_mixin.get_closer_driver.return_value = 'johny'

                        mock_directions.return_value = Mock()
                        mock_directions.return_value.ok = True
                        mock_directions.return_value.json.return_value = {
                            'routes': [
                                {
                                    'overview_polyline': {
                                        'points':   "fe}qEbtwcJsBhBmBsD}BkEcBkDc@cAYa@jC{E`@}@"
                                                    "jBwDl@wBh@yBHQNa@r@_B|@eBZi@d@kAfBmFXuA^q"
                                                    "B^qBd@{Cl@_GDu@L}BCQKc@V{BL}@\\aBZmAt@qBx"
                                                    "GwMbC{E|BwE~A"
                                    }
                                }
                            ]
                        }

                        response = self.client.post(
                            '/riders/joe_smith/request',
                            data=json.dumps(dict(
                                latitude_initial=30.00,
                                latitude_final=31.32,
                                longitude_initial=42,
                                longitude_final=43.21
                            )),
                            headers=dict(
                                Authorization='Bearer ' + self.rider_joe_auth_token
                            ),
                            content_type='application/json'
                        )
                        data = json.loads(response.data.decode())
                    self.request_id = data['id']

    def test_should_be_authenticated(self):

        with self.client:
            response = self.client.delete(
                '/requests/{}'.format(self.request_id),
                headers=dict(
                    Authorization='Bearer avFalseToken123'
                ),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'invalid_token')

            self.assertEqual(data['status'], 'fail')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 401)

    def test_should_be_someone_related_to_request(self):
        with self.client:
            response = self.client.delete(
                '/requests/{}'.format(self.request_id),
                headers=dict(
                    Authorization='Bearer ' + self.rider_will_auth_token
                ),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'unauthorized_action')

            self.assertEqual(data['status'], 'fail')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 401)


    def test_request_should_exist(self):
        with self.client:
            response = self.client.delete(
                '/requests/5a1e175ed3a5fe3cd99e010b',
                headers=dict(
                    Authorization='Bearer ' + self.rider_joe_auth_token
                ),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'no_request_found')

            self.assertEqual(data['status'], 'fail')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 404)


    def test_request_cancellation(self):
        with self.client:
            response = self.client.delete(
                '/requests/{}'.format(self.request_id),
                headers=dict(
                    Authorization='Bearer ' + self.rider_joe_auth_token
                ),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'request_cancelled')

            self.assertEqual(data['status'], 'success')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 203)
