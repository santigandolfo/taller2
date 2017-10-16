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
        mock_request.return_value.json.return_value = {
                            "metadata": {
                                "version": "string"
                            },
                            "auth_token": "fasdasfdsafsd.fdsafdsa.fdsafsdafdsa",
                            "user": {
                                "id": "1",
                                "_ref": "2",
                                "applicationOwner": "fiuber",
                                "type": "driver",
                                "cars": [
                                {
                                    "id": "2",
                                    "_ref": "3",
                                    "owner": "carlosc",
                                    "properties": [
                                    {
                                        "name": "string",
                                        "value": "string"
                                    }
                                    ]
                                }
                                ],
                                "username": "carlosc",
                                "name": "Carlos",
                                "surname": "Carloso",
                                "country": "Argentina",
                                "email": "carlos@gmail.com",
                                "birthdate": "23-10-2017",
                                "images": [
                                "fdlsakflsdak"
                                ],
                                "balance": [
                                {
                                    "currency": "ARS",
                                    "value": 0
                                }
                                ]
                            }
                            }
        mock_request.return_value.ok = True
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({
                                "type": "driver",
                                "cars": [
                                {
                                    "id": "2",
                                    "_ref": "3",
                                    "owner": "carlosc",
                                    "properties": [
                                    {
                                        "name": "string",
                                        "value": "string"
                                    }
                                    ]
                                }
                                ],
                                "username": "carlosc",
                                "password": "12345678",
                                "name": "Carlos",
                                "surname": "Carloso",
                                "country": "Argentina",
                                "email": "carlos@gmail.com",
                                "birthdate": "23-10-2017",
                                "images": [
                                "fdlsakflsdak"
                                ],
                                "balance": [
                                {
                                    "currency": "ARS",
                                    "value": 0
                                }
                                ]
                            }
                            ),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'user_registered')
            self.assertEqual(data['status'],'success')
            self.assertEqual(data['info'], 
                            {
                                "id": "1",
                                "_ref": "2",
                                "applicationOwner": "fiuber",
                                "type": "driver",
                                "cars": [
                                {
                                    "id": "2",
                                    "_ref": "3",
                                    "owner": "carlosc",
                                    "properties": [
                                    {
                                        "name": "string",
                                        "value": "string"
                                    }
                                    ]
                                }
                                ],
                                "username": "carlosc",
                                "name": "Carlos",
                                "surname": "Carloso",
                                "country": "Argentina",
                                "email": "carlos@gmail.com",
                                "birthdate": "23-10-2017",
                                "images": [
                                "fdlsakflsdak"
                                ],
                                "balance": [
                                {
                                    "currency": "ARS",
                                    "value": 0
                                }
                                ]
                            }
                            )
            self.assertEqual(data['message'],'user_registered')
            self.assertTrue(data['auth_token'])
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 201)
    @patch('requests.post')
    def test_registration_with_minimum_info(self, mock_request):
        """ Test for user registration """

        mock_request.return_value = Mock()
        mock_request.return_value.json.return_value = {'status':'success','message':'user_registered','auth_token':'fmsdakfkldskafl.fdsalfkdsa.fdsafsd', "user":{"username":"joe_smith"}}
        mock_request.return_value.ok = True
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(dict(
                    username='joe_smith',
                    password='123456'
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
                    password='123456'
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
                    password='123456'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(
                data['message'], 'invalid_username')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 400)
    
    def test_register_with_missing_password(self):
        """ Test registration without password"""
        
        with self.client:
            
            response = self.client.post(
                '/users',
                data=json.dumps(dict(
                    username='joe_smith',
                    pssword='123456'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(
                data['message'], 'missing_password')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 400)




# class TestDelete(BaseTestCase):
#     def test_delete_user_correctly(self):
#         """ Test for user delete, correct case """
#         with self.client:
#             response = self.client.post(
#                 '/users',
#                 data=json.dumps(dict(
#                     username='joe_smith',
#                     password='123456'
#                 )),
#                 content_type='application/json'
#             )
#             data = json.loads(response.data.decode())
#             self.assertTrue(data['status'] == 'success')
#             self.assertTrue(data['message'] == 'user_registered')
#             self.assertTrue(data['auth_token'])
#             self.assertTrue(response.content_type == 'application/json')
#             self.assertEqual(response.status_code, 201)
#             response = self.client.delete(
#                 '/users',
#                 headers=dict(
#                     Authorization='Bearer ' + data['auth_token']
#                 ),
#                 content_type='application/json'
#             )
#             data = json.loads(response.data.decode())
#             self.assertTrue(data['status'] == 'success')
#             self.assertTrue(data['message'] == 'user_deleted')
#             self.assertTrue(response.content_type == 'application/json')
#             self.assertEqual(response.status_code, 203)

#     def test_delete_without_token(self):
#         """ Test for trying to delete user without loging in """
#         with self.client:
#             response = self.client.post(
#                 '/users',
#                 data=json.dumps(dict(
#                     username='joe_smith',
#                     password='123456'
#                 )),
#                 content_type='application/json'
#             )
#             data = json.loads(response.data.decode())
#             response = self.client.delete(
#                 '/users',
#                 content_type='application/json'
#             )
#             data = json.loads(response.data.decode())
#             self.assertTrue(data['status'] == 'fail')
#             self.assertTrue(data['message'] == 'missing_token')
#             self.assertTrue(response.content_type == 'application/json')
#             self.assertEqual(response.status_code, 401)

#     def test_delete_with_expired_token(self):
#         """ Test for trying to delete user with expired token """
#         with self.client:
#             response = self.client.post(
#                 '/users',
#                 data=json.dumps(dict(
#                     username='joe_smith',
#                     password='123456'
#                 )),
#                 content_type='application/json'
#             )
#             data = json.loads(response.data.decode())
#             time.sleep(TOKEN_DURATION+1)
#             response = self.client.delete(
#                 '/users',
#                 headers=dict(
#                     Authorization='Bearer ' + data['auth_token']
#                 ),
#                 content_type='application/json'
#             )
#             data = json.loads(response.data.decode())
#             self.assertTrue(data['status'] == 'fail')
#             self.assertTrue(data['message'] == 'expired_token')
#             self.assertTrue(response.content_type == 'application/json')
#             self.assertEqual(response.status_code, 401)
#     def test_delete_with_invalid_token(self):
#         """ Test for trying to delete user with invalid token """
#         with self.client:
#             response = self.client.post(
#                 '/users',
#                 data=json.dumps(dict(
#                     username='joe_smith',
#                     password='123456'
#                 )),
#                 content_type='application/json'
#             )
#             data = json.loads(response.data.decode())

#             response = self.client.delete(
#                 '/users',
#                 headers=dict(
#                     Authorization='Bearer ' + u'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJsb2dnZWRJbkFzIjoiYWRtaW4iLCJpYXQiOjE0MjI3Nzk2Mzh9.gzSraSYS8EXBxLN_oWnFSRgCzcmJmMjLiuyu5CSpyHI'
#                 ),
#                 content_type='application/json'
#             )
#             data = json.loads(response.data.decode())
#             self.assertTrue(data['status'] == 'fail')
#             self.assertTrue(data['message'] == 'invalid_token')
#             self.assertTrue(response.content_type == 'application/json')
#             self.assertEqual(response.status_code, 401)


#     def test_delete_already_deleted_user(self):
#         """ Test for trying to delete user which was already deleted """
#         with self.client:
#             response = self.client.post(
#                 '/users',
#                 data=json.dumps(dict(
#                     username='joe_smith',
#                     password='123456'
#                 )),
#                 content_type='application/json'
#             )
#             data = json.loads(response.data.decode())
#             auth_token = data['auth_token']
#             response = self.client.delete(
#                 '/users',
#                 headers=dict(
#                     Authorization='Bearer ' + auth_token
#                 ),
#                 content_type='application/json'
#             )
#             response = self.client.delete(
#                 '/users',
#                 headers=dict(
#                     Authorization='Bearer ' + auth_token
#                 ),
#                 content_type='application/json'
#             )
#             data = json.loads(response.data.decode())
#             self.assertTrue(data['status'] == 'fail')
#             self.assertTrue(data['message'] == 'no_user_found')
#             self.assertTrue(response.content_type == 'application/json')
#             self.assertEqual(response.status_code, 404)
  
if __name__ == '__main__':
    unittest.main()
