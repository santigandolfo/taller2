import unittest
import json
import time
from mock import patch, Mock
from src.models import User
from tests.base import BaseTestCase
from app import application, TOKEN_DURATION


class TestLogin(BaseTestCase):
    def test_login_empty_username(self):
        """ Test login with empty username"""
        with self.client:

            response = self.client.post(
                '/security',
                data=json.dumps(dict(
                    username='',
                    password='123456'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'missing_username')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 400)

    def test_login_missing_username(self):
        """ Test login without username"""
        with self.client:

            response = self.client.post(
                '/security',
                data=json.dumps(dict(
                    username='',
                    password='123456'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'missing_username')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 400)

    def test_login_with_missing_password(self):
        """ Test login without password"""

        with self.client:

            response = self.client.post(
                '/security',
                data=json.dumps(dict(
                    username='joe_smith',
                    password=''
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'missing_password')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 400)

    def test_login_unregistered_user(self):
        """ Test login from an unregistered user"""

        with self.client:

            response = self.client.post(
                '/security',
                data=json.dumps(dict(
                    username='unregistered',
                    password='54321'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'unregistered_user')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 409)

    def test_login_with_wrong_password(self):
        """ Test login from a registered user with wrong password"""

        with self.client:
            with patch('requests.post') as mock_post:
                mock_post.return_value = Mock()
                mock_post.return_value.json.return_value = {'id':"1"}
                mock_post.return_value.ok = True
                mock_post.return_value.status_code = 201
                self.client.post(
                    '/users',
                    data=json.dumps(dict(
                        username='juan_perez',
                        password='perez20',
                        type='passenger'
                    )),
                    content_type='application/json'
                )

                mock_post.return_value = Mock()
                mock_post.return_value.json.return_value = {'status':'success','message':'user_registered','auth_token':'fmsdakfkldskafl.fdsalfkdsa.fdsafsd', "user":{"username":"joe_smith"}}
                mock_post.return_value.ok = False
                mock_post.return_value.status_code = 401

                response = self.client.post(
                    '/security',
                    data=json.dumps(dict(
                        username='juan_perez',
                        password='perez21'
                    )),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                self.assertEqual(data['status'], 'fail')
                self.assertEqual(data['message'], 'wrong_password')
                self.assertEqual(response.content_type, 'application/json')
                self.assertEqual(response.status_code, 401)

    def test_succesful_login(self):
        """ Test login from a registered user with correct password"""

        with self.client:
            with patch('requests.post') as mock_post:
                mock_post.return_value = Mock()
                mock_post.return_value.json.return_value = {'id':"1"}
                mock_post.return_value.ok = True
                mock_post.return_value.status_code = 201
                self.client.post(
                    '/users',
                    data=json.dumps(dict(
                        username='juan_perez',
                        password='perez20',
                        type='driver'
                    )),
                    content_type='application/json'
                )
                mock_post.return_value = Mock()
                mock_post.return_value.json.return_value = {'status':'success','message':'valid_credentials','auth_token':'fmsdakfkldskafl.fdsalfkdsa.fdsafsd'}
                mock_post.return_value.ok = True
                mock_post.return_value.status_code = 200
                response = self.client.post(
                    '/security',
                    data=json.dumps(dict(
                        username='juan_perez',
                        password='perez20'
                    )),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                self.assertEqual(data['status'], 'success')
                self.assertEqual(data['message'], 'login_succesful')
                self.assertTrue(data['auth_token'])
                self.assertEqual(response.content_type, 'application/json')
                self.assertEqual(response.status_code, 200)



class TestLogout(BaseTestCase):

    def test_succesful_logout_after_register(self):
        """ Test logout from a recently registered user"""
        auth_token = ''
        with self.client:
            with patch('requests.post') as mock_post:
                mock_post.return_value = Mock()
                mock_post.return_value.json.return_value = {'id':"1"}
                mock_post.return_value.ok = True
                mock_post.return_value.status_code = 201
                response = self.client.post(
                    '/users',
                    data=json.dumps(dict(
                        username='pedro_gomez',
                        password='peritomoreno',
                        type='passenger'
                    )),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                auth_token = data['auth_token']
            with patch('requests.post') as mock_post:
                mock_post.return_value = Mock()
                mock_post.return_value.ok = True
                mock_post.return_value.status_code = 200
                response = self.client.delete(
                    '/security',
                    headers=dict(
                        Authorization='Bearer ' + auth_token
                    ),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                self.assertEqual(data['status'], 'success')
                self.assertEqual(data['message'], 'logout_succesful')
                self.assertEqual(response.content_type, 'application/json')
                self.assertEqual(response.status_code, 200)

    def test_succesful_logout_after_login(self):
        """ Test logout from a recently logged in user"""
        auth_token = ''
        with self.client:
            with patch('requests.post') as mock_post:
                mock_post.return_value = Mock()
                mock_post.return_value.json.return_value = {'id':"1"}
                mock_post.return_value.ok = True
                mock_post.return_value.status_code = 201
                self.client.post(
                    '/users',
                    data=json.dumps(dict(
                        username='pedro_gomez',
                        password='peritomoreno',
                        type='passenger'
                    )),
                    content_type='application/json'
                )

            with patch('requests.post') as mock_post:
                mock_post.return_value = Mock()
                mock_post.return_value.json.return_value = {'status':'success','message':'succesful_login','auth_token':'fmsdakfkldskafl.fdsalfkdsa.fdsafsd'}
                mock_post.return_value.ok = True
                mock_post.return_value.status_code = 200
                response = self.client.post(
                    '/security',
                    data=json.dumps(dict(
                        username='pedro_gomez',
                        password='peritomoreno'
                    )),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                auth_token = data['auth_token']


            with patch('requests.delete') as mock_delete:
                mock_delete.return_value = Mock()
                mock_delete.return_value.ok = True
                mock_delete.return_value.status_code = 200
                response = self.client.delete(
                    '/security',
                    headers=dict(
                        Authorization='Bearer ' + auth_token
                    ),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                self.assertEqual(data['status'], 'success')
                self.assertEqual(data['message'], 'logout_succesful')
                self.assertEqual(response.content_type, 'application/json')
                self.assertEqual(response.status_code, 200)

    def test_logout_without_a_token(self):
        """ Test logout without a token"""

        with self.client:

            response = self.client.delete(
                '/security',
                data=json.dumps(dict(
                    username='juan_perez',
                    password='perez20'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'missing_token')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 400)

    def test_logout_with_empty_token(self):
        """ Test logout with an empty token"""

        with self.client:

            response = self.client.delete(
                '/security',
                headers=dict(
                    Authorization='Bearer ' + ''
                ),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'missing_token')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 400)

    def test_logout_with_invalid_token(self):
        """ Test logout with a string as token"""

        with self.client:

            response = self.client.delete(
                '/security',
                headers=dict(
                    Authorization='Bearer ' + 'ab7873olP'
                ),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'invalid_token')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 401)

    def test_logout_with_expired_token(self):
        """ Test logout with an expired token"""

        with self.client:
            with patch('requests.post') as mock_post:
                mock_post.return_value = Mock()
                mock_post.return_value.json.return_value = {'id':"1"}
                mock_post.return_value.ok = True
                mock_post.return_value.status_code = 201
                response = self.client.post(
                    '/users',
                    data=json.dumps(dict(
                        username='pedro_gomez',
                        password='peritomoreno',
                        type='driver'
                    )),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                time.sleep(1+TOKEN_DURATION)
                mock_post.return_value = Mock()
                mock_post.return_value.ok = True
                mock_post.return_value.status_code = 200
                response = self.client.delete(
                    '/security',
                    headers=dict(
                        Authorization='Bearer ' + data['auth_token']
                    ),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                self.assertEqual(data['status'], 'fail')
                self.assertEqual(data['message'], 'expired_token')
                self.assertEqual(response.content_type, 'application/json')
                self.assertEqual(response.status_code, 401)

    def test_logout_with_malformed_authorization_header(self):
        """ Test logout with a malformed authorization header"""

        with self.client:

            response = self.client.delete(
                '/security',
                headers=dict(
                    Authorization='ab7873olP' #Bearer missing
                ),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'internal_error')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 500)

if __name__ == '__main__':
    unittest.main()
