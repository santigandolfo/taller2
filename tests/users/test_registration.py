# project/tests/test_auth.py

import unittest
import json
import time
from src.models import User
from tests.base import BaseTestCase
from mock import patch,Mock
from app import application, TOKEN_DURATION

class TestRegistration(BaseTestCase):
    @patch('requests.post')
    def test_registration_with_maximum_info(self, mock_request):
        """ Test for user registration """

        mock_request.return_value = Mock()
        mock_request.return_value.json.return_value = {'id':"1"}
        mock_request.return_value.ok = True
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({
                      'username':"fedebalina",
                      'password':"picapiedra",
                      'firstname':"Federico",
                      'lastname':"Balina",
                      'email':"federicobalina@gmail.com",
                      'birthdate':"05/06/1995",
                      'type':"driver",
                      'country':"Argentina",
                      'image':"iVBORw0KGgoAAAANSUhEUgAABOEAAATrCAYAAADbvqaNAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAIGNIUk0AAHolAACAgwAA+f8AAIDpAAB1MAAA6mAAADqYAAAXb5JfxUYACbM5SURBVHja7P3ZkiRX"
                            }
                            ),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'user_registered')
            self.assertEqual(data['status'],'success')
            self.assertTrue(data['auth_token'])
            self.assertEqual(data['id'],"1")
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 201)
    @patch('requests.post')
    def test_registration_with_minimum_info(self, mock_request):
        """ Test for user registration """

        mock_request.return_value = Mock()
        mock_request.return_value.json.return_value = {'id':"1"}
        mock_request.return_value.ok = True
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(dict(
                    username='joe_smith',
                    password='123456',
                    email='joesmith@gmail.com',
                    type='passenger'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'user_registered')
            self.assertEqual(data['status'], 'success')
            self.assertTrue(data['auth_token'])
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 201)

    @patch('requests.post')
    def test_registered_with_already_registered_user(self, mock_request):
        """ Test registration with already registered username"""
        with self.client:
            response = ''
            mock_request.return_value = Mock()
            mock_request.return_value.json.return_value = {'status':'fail','message':'user_username_already_exists'}
            mock_request.return_value.ok = False
            mock_request.return_value.status_code = 409
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
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(
                data['message'], 'user_username_already_exists')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 409)

    def test_register_with_missing_username(self):
        """ Test registration without an username"""

        with self.client:

            response = self.client.post(
                '/users',
                data=json.dumps(dict(
                    emal='joe_smith',
                    password='123456',
                    type='passenger'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'],'invalid_username')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 400)

    def test_register_with_missing_password(self):
        """ Test registration without password"""

        with self.client:

            response = self.client.post(
                '/users',
                data=json.dumps(dict(
                    username='joe_smith',
                    pssword='123456',
                    type='passenger'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(
                data['message'], 'missing_password')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 400)




class TestDelete(BaseTestCase):
    @patch('requests.post')
    @patch('requests.delete')
    def test_delete_user_correctly(self, mock_delete, mock_post):
        """ Test for user delete, correct case """
        mock_post.return_value = Mock()
        mock_post.return_value.json.return_value = {'id':"1"}
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 201

        mock_delete.return_value = Mock()
        mock_delete.return_value.json.return_value = {'status':'success','message':'user_removed'}
        mock_delete.return_value.ok = True
        mock_delete.return_value.status_code = 203
        with self.client:


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

            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'user_registered')
            self.assertTrue(data['auth_token'])
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 201)


            response = self.client.delete(
                '/users/joe_smith',
                headers=dict(
                    Authorization='Bearer ' + data['auth_token']
                ),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'user_deleted')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 203)

    @patch('requests.post')
    def test_delete_without_token(self,mock_post):
        """ Test for trying to delete user without loging in """

        mock_post.return_value = Mock()
        mock_post.return_value.json.return_value = {'id':"1"}
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 201
        with self.client:

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
            response = self.client.delete(
                '/users/joe_smith',
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'missing_token')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 401)

    @patch('requests.post')
    def test_delete_with_expired_token(self,mock_post):
        """ Test for trying to delete user with expired token """
        mock_post.return_value = Mock()
        mock_post.return_value.json.return_value = {'id':"1"}
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 201
        with self.client:
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
            time.sleep(TOKEN_DURATION+1)
            response = self.client.delete(
                '/users/joe_smith',
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

    @patch('requests.post')
    def test_delete_with_invalid_token(self,mock_post):
        """ Test for trying to delete user with invalid token """
        mock_post.return_value = Mock()
        mock_post.return_value.json.return_value = {'id':"1"}
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 201
        with self.client:
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

            response = self.client.delete(
                '/users/joe_smith',
                headers=dict(
                    Authorization='Bearer ' + u'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJsb2dnZWRJbkFzIjoiYWRtaW4iLCJpYXQiOjE0MjI3Nzk2Mzh9.gzSraSYS8EXBxLN_oWnFSRgCzcmJmMjLiuyu5CSpyHI'
                ),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'invalid_token')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    unittest.main()
