import unittest
import json
import time
from tests.base import BaseTestCase
from mock import patch, Mock
from app import TOKEN_DURATION

class TestDriversCarRegistration(BaseTestCase):
    def test_add_car_succesfully(self):
        """Add car information for a registered driver succesfully"""
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

                response = self.client.post(
                    '/drivers/joe_smith/cars',
                    headers=dict(
                        Authorization='Bearer ' + auth_token
                    ),
                    data=json.dumps(dict(
                        brand='peugeot',
                        color='black',
                        model='207',
                        year=2016
                    )),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                self.assertEqual(data['status'], 'success')
                self.assertEqual(data['message'], 'car_registered_succesfully')
                self.assertEqual(data['car_id'], "1")
                self.assertEqual(response.content_type, 'application/json')
                self.assertEqual(response.status_code, 200)

    def test_add_car_to_a_passenger(self):
        """Add car information for a registered passenger"""
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

                response = self.client.post(
                    '/drivers/joe_smith/cars',
                    headers=dict(
                        Authorization='Bearer ' + auth_token
                    ),
                    data=json.dumps(dict(
                        brand='peugeot',
                        color='black',
                        model='207',
                        year=2016
                    )),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                self.assertEqual(data['status'], 'fail')
                self.assertEqual(data['message'], 'driver_not_found')
                self.assertEqual(response.content_type, 'application/json')
                self.assertEqual(response.status_code, 404)

    def test_add_car_to_an_unregistered_user(self):
        """Add car information for an unregistered user"""
        with self.client:
            response = self.client.post(
                '/drivers/joe_smith/cars',
                headers=dict(
                    Authorization='Bearer '
                ),
                data=json.dumps(dict(
                    brand='peugeot',
                    color='black',
                    model='207',
                    year=2016
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'driver_not_found')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 404)

    def test_add_car_unauthorized_user(self):
        """Add car information by an unauthorized user"""
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
                response = self.client.post(
                    '/users',
                    data=json.dumps(dict(
                        username='pablo_perez',
                        password='123456',
                        type='passenger'
                    )),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                auth_token = data['auth_token']

                response = self.client.post(
                    '/drivers/joe_smith/cars',
                    headers=dict(
                        Authorization='Bearer ' + auth_token
                    ),
                    data=json.dumps(dict(
                        brand='peugeot',
                        color='black',
                        model='207',
                        year=2016
                    )),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                self.assertEqual(data['status'], 'fail')
                self.assertEqual(data['message'], 'unauthorized_action')
                self.assertEqual(response.content_type, 'application/json')
                self.assertEqual(response.status_code, 401)

    def test_add_car_missing_token(self):
        """Add car information without a token"""
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
                    content_type='application/json')
                auth_token = ''
                response = self.client.post(
                    '/drivers/joe_smith/cars',
                    headers=dict(
                        Authorization='Bearer ' + auth_token
                    ),
                    data=json.dumps(dict(
                        brand='peugeot',
                        color='black',
                        model='207',
                        year=2016
                    )),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                self.assertEqual(data['status'], 'fail')
                self.assertEqual(data['message'], 'missing_token')
                self.assertEqual(response.content_type, 'application/json')
                self.assertEqual(response.status_code, 401)

    def test_add_car_expired_token(self):
        """Add car information with an expired token"""
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
                time.sleep(TOKEN_DURATION + 1)
                response = self.client.post(
                    '/drivers/joe_smith/cars',
                    headers=dict(
                        Authorization='Bearer ' + auth_token
                    ),
                    data=json.dumps(dict(
                        brand='peugeot',
                        color='black',
                        model='207',
                        year=2016
                    )),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                self.assertEqual(data['status'], 'fail')
                self.assertEqual(data['message'], 'expired_token')
                self.assertEqual(response.content_type, 'application/json')
                self.assertEqual(response.status_code, 401)

    def test_add_car_invalid_token(self):
        """Add car information with an invalid token"""
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
                response = self.client.post(
                    '/drivers/joe_smith/cars',
                    headers=dict(
                        Authorization='Bearer aaaaa'
                    ),
                    data=json.dumps(dict(
                        brand='peugeot',
                        color='black',
                        model='207',
                        year=2016
                    )),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                self.assertEqual(data['status'], 'fail')
                self.assertEqual(data['message'], 'invalid_token')
                self.assertEqual(response.content_type, 'application/json')
                self.assertEqual(response.status_code, 401)

class TestDriversCarDeletion(BaseTestCase):
    def test_delete_car_succesfully(self):
        """Delete car information for a registered driver with a registered car succesfully"""
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

                response = self.client.post(
                    '/drivers/joe_smith/cars',
                    headers=dict(
                        Authorization='Bearer ' + auth_token
                    ),
                    data=json.dumps(dict(
                        brand='peugeot',
                        color='black',
                        model='207',
                        year=2016
                    )),
                    content_type='application/json'
                )
            with patch('requests.delete') as mock_delete:
                mock_delete.return_value = Mock()
                mock_delete.return_value.ok = True
                mock_delete.return_value.status_code = 200
                response = self.client.delete(
                    '/drivers/joe_smith/cars/1',
                    headers=dict(
                        Authorization='Bearer ' + auth_token
                    ),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                #self.assertEqual(data['status'], 'success')
                self.assertEqual(data['message'], 'car_deleted_succesfully')
                self.assertEqual(response.content_type, 'application/json')
                self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
