import unittest
import json
import time
from tests.base import BaseTestCase
from mock import patch, Mock
from app import TOKEN_DURATION


class TestPosition(BaseTestCase):
    def test_update_position_correctly(self):
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
                        type='passenger'
                    )),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                auth_token = data['auth_token']

            response = self.client.put(
                '/users/joe_smith/coordinates',
                headers=dict(
                    Authorization='Bearer ' + auth_token
                ),
                data=json.dumps(dict(
                    latitude='43.232',
                    longitude='125.334'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'position_updated')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 200)

    def test_update_position_correctly_twice(self):
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
                        type='passenger'
                    )),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                auth_token = data['auth_token']

            self.client.put(
                '/users/joe_smith/coordinates',
                headers=dict(
                    Authorization='Bearer ' + auth_token
                ),
                data=json.dumps(dict(
                    latitude='43.232',
                    longitude='125.334'
                )),
                content_type='application/json'
            )
            response = self.client.put(
                '/users/joe_smith/coordinates',
                headers=dict(
                    Authorization='Bearer ' + auth_token
                ),
                data=json.dumps(dict(
                    latitude='54.232',
                    longitude='176.324'
                )),
                content_type='application/json'
            )

            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'position_updated')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 200)

    def test_update_position_bad_request_no_longitude(self):
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
                        type='driver'
                    )),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                auth_token = data['auth_token']

            response = self.client.put(
                '/users/joe_smith/coordinates',
                headers=dict(
                    Authorization='Bearer ' + auth_token
                ),
                data=json.dumps(dict(
                    latitude='43.232',
                    logitude='125.334'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'bad_request_data')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 400)

    def test_update_position_bad_request_invalid_latitude(self):
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
                        type='passenger'
                    )),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                auth_token = data['auth_token']

            response = self.client.put(
                '/users/joe_smith/coordinates',
                headers=dict(
                    Authorization='Bearer ' + auth_token
                ),
                data=json.dumps(dict(
                    latitude='93.232',
                    longitude='125.334'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'bad_request_data')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 400)

    def test_update_position_user_not_found(self):
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
                        type='passenger'
                    )),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                auth_token = data['auth_token']

            response = self.client.put(
                '/users/joel_smith/coordinates',
                headers=dict(
                    Authorization='Bearer ' + auth_token
                ),
                data=json.dumps(dict(
                    latitude='43.232',
                    longitude='125.334'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'user_not_found')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 404)

    def test_update_position_missing_token(self):
        with self.client:
            with patch('requests.post') as mock_post:
                mock_post.return_value = Mock()
                mock_post.return_value.json.return_value = {'id': "1"}
                mock_post.return_value.ok = True
                mock_post.return_value.status_code = 201
                self.client.post(
                    '/users',
                    data=json.dumps(dict(
                        username='joe_smith',
                        password='123456',
                        type='driver'
                    )),
                    content_type='application/json'
                )
            response = self.client.put(
                '/users/joe_smith/coordinates',
                headers=dict(
                    Authorization='Bearer '
                ),
                data=json.dumps(dict(
                    latitude='43.232',
                    longitude='125.334'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'missing_token')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 401)

    def test_update_position_invalid_token(self):
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
                        type='passenger'
                    )),
                    content_type='application/json'
                )

            response = self.client.put(
                '/users/joe_smith/coordinates',
                headers=dict(
                    Authorization='Bearer asndo3i435i1242ijfeadjs'
                ),
                data=json.dumps(dict(
                    latitude='43.232',
                    longitude='125.334'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'invalid_token')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 401)

    def test_update_position_expired_token(self):
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
                        type='passenger'
                    )),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                auth_token = data['auth_token']

            time.sleep(TOKEN_DURATION + 1)
            response = self.client.put(
                '/users/joe_smith/coordinates',
                headers=dict(
                    Authorization='Bearer ' + auth_token
                ),
                data=json.dumps(dict(
                    latitude='43.232',
                    longitude='125.334'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'expired_token')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 401)

    def test_update_position_unauthorized_user(self):
        with self.client:
            with patch('requests.post') as mock_post:
                mock_post.return_value = Mock()
                mock_post.return_value.json.return_value = {'id': "1"}
                mock_post.return_value.ok = True
                mock_post.return_value.status_code = 201
                self.client.post(
                    '/users',
                    data=json.dumps(dict(
                        username='pablo_perez',
                        password='123456',
                        type='driver'
                    )),
                    content_type='application/json'
                )
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
                        type='passenger'
                    )),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                auth_token = data['auth_token']
            response = self.client.put(
                '/users/pablo_perez/coordinates',
                headers=dict(
                    Authorization='Bearer ' + auth_token
                ),
                data=json.dumps(dict(
                    latitude='43.232',
                    longitude='125.334'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'unauthorized_update')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    unittest.main()
