import unittest
import json
import time
from src.models import User
from tests.base import BaseTestCase
from app import application

TOKEN_TIME = 5 #TODO: Setear segun duracion token

class TestLogin(BaseTestCase):
    def test_login_empty_email(self):
        """ Test login with empty email"""
        with self.client:

            response = self.client.post(
                '/security',
                data=json.dumps(dict(
                    email='',
                    password='123456'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'missing_email')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 400)

    def test_login_missing_email(self):
        """ Test login without email"""
        with self.client:

            response = self.client.post(
                '/security',
                data=json.dumps(dict(
                    email='',
                    password='123456'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'missing_email')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 400)

    def test_login_with_missing_password(self):
        """ Test login without password"""

        with self.client:

            response = self.client.post(
                '/security',
                data=json.dumps(dict(
                    email='joe@gmail.com',
                    password=''
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'missing_password')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 400)

    def test_login_unregistered_user(self):
        """ Test login from an unregistered user"""

        with self.client:

            response = self.client.post(
                '/security',
                data=json.dumps(dict(
                    email='unregistered@gmail.com',
                    password='54321'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'unregistered_user')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 409)

    def test_login_with_wrong_password(self):
        """ Test login from a registered user with wrong password"""

        with self.client:

            self.client.post(
                '/users',
                data=json.dumps(dict(
                    email='juan@gmail.com',
                    password='perez20'
                )),
                content_type='application/json'
            )
            response = self.client.post(
                '/security',
                data=json.dumps(dict(
                    email='juan@gmail.com',
                    password='perez21'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'wrong_password')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 401)

    def test_succesful_login(self):
        """ Test login from a registered user with correct password"""

        with self.client:

            self.client.post(
                '/users',
                data=json.dumps(dict(
                    email='juan@gmail.com',
                    password='perez20'
                )),
                content_type='application/json'
            )
            response = self.client.post(
                '/security',
                data=json.dumps(dict(
                    email='juan@gmail.com',
                    password='perez20'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'login_succesful')
            self.assertTrue(data['auth_token'])
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 201)



class TestLogout(BaseTestCase):
    def test_succesful_logout_after_register(self):
        """ Test logout from a recently registered user"""

        with self.client:

            response = self.client.post(
                '/users',
                data=json.dumps(dict(
                    email='pedro@gmail.com',
                    password='peritomoreno'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            response = self.client.delete(
                '/security',
                headers=dict(
                    Authorization='Bearer ' + data['auth_token']
                ),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'logout_succesful')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 200)

    def test_succesful_logout_after_login(self):
        """ Test logout from a recently logged in user"""

        with self.client:
            self.client.post(
                '/users',
                data=json.dumps(dict(
                    email='pedro@gmail.com',
                    password='peritomoreno'
                )),
                content_type='application/json'
            )
            response = self.client.post(
                '/security',
                data=json.dumps(dict(
                    email='pedro@gmail.com',
                    password='peritomoreno'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            response = self.client.delete(
                '/security',
                headers=dict(
                    Authorization='Bearer ' + data['auth_token']
                ),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'logout_succesful')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 200)

    def test_logout_without_a_token(self):
        """ Test logout without a token"""

        with self.client:

            response = self.client.delete(
                '/security',
                data=json.dumps(dict(
                    email='juan@gmail.com',
                    password='perez20'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'missing_token')
            self.assertTrue(response.content_type == 'application/json')
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
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'missing_token')
            self.assertTrue(response.content_type == 'application/json')
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
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'invalid_token')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 401)

    def test_logout_with_expired_token(self):
        """ Test logout with an expired token"""

        with self.client:

            response = self.client.post(
                '/users',
                data=json.dumps(dict(
                    email='pedro@gmail.com',
                    password='peritomoreno'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            time.sleep(1.2*TOKEN_TIME)
            response = self.client.delete(
                '/security',
                headers=dict(
                    Authorization='Bearer ' + data['auth_token']
                ),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'expired_token')
            self.assertTrue(response.content_type == 'application/json')
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
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'internal_error')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 500)

if __name__ == '__main__':
    unittest.main()
