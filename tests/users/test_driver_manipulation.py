import unittest
import json
import time
from src.models import User
from tests.base import BaseTestCase
from mock import patch,Mock
from app import application, TOKEN_DURATION

class TestDriverManipulation(BaseTestCase):

    @patch('requests.post')
    def test_simple_data_update(self, mock_post):
        """ Test case for a simple availability change"""
        mock_post.return_value = Mock()
        mock_post.return_value.json.return_value = {'status':'success','message':'user_registered','auth_token':'fmsdakfkldskafl.fdsalfkdsa.fdsafsd', "user":{"username":"joe_smith"}}
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 201
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(dict(
                    username='pedro',
                    password='123456'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            auth_token = data['auth_token']
            response = self.client.patch(
                '/drivers',
                data=json.dumps(dict(
                    availability=True
                )),
                headers=dict(
                    Authorization='Bearer '+auth_token
                ),
                content_type='application/json'

                )
            
            data = json.loads(response.data.decode())

            self.assertEqual(data['status'],'success')
            self.assertEqual(data['message'],'changed_availability')
            self.assertEqual(response.content_type,'application/json')
            self.assertEqual(response.status_code,200)
    @patch('requests.post')
    @patch('requests.get')
    def test_one_driver_available(self, mock_get, mock_post):
        """Make a driver available, request of available drivers should display it"""
        mock_post.return_value = Mock()
        mock_post.return_value.json.return_value = {'status':'success','message':'user_registered','auth_token':'fmsdakfkldskafl.fdsalfkdsa.fdsafsd', "user":{"username":"joe_smith"}}
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 201
        mock_get.return_value = Mock()
        mock_get.return_value.json.return_value = {'username':'carlos'}
        mock_get.return_value.ok = True
        mock_get.return_value.status_code = 201
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(dict(
                    username='pedro',
                    password='123456'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            auth_token = data['auth_token']
            response = self.client.patch(
                '/drivers',
                data=json.dumps(dict(
                    availability=True
                )),
                headers=dict(
                    Authorization='Bearer '+auth_token
                ),
                content_type='application/json'

                )
            data = json.loads(response.data.decode())
            response = self.client.get('/drivers/available')
            drivers = json.loads(response.data.decode())
            self.assertEqual(response.content_type,'application/json')
            self.assertEqual(response.status_code,200)
            self.assertTrue(isinstance(drivers,list))
            self.assertEqual(len(drivers), 1)
            self.assertEqual(drivers[0]['username'],'carlos')
    
    
    @patch('requests.post')
    @patch('requests.get')
    def test_one_driver_not_availabe(self, mock_get, mock_post):
        """Make a driver available, then make it unavailable, request of available drivers should not display it"""
        mock_post.return_value = Mock()
        mock_post.return_value.json.return_value = {'status':'success','message':'user_registered','auth_token':'fmsdakfkldskafl.fdsalfkdsa.fdsafsd', "user":{"username":"joe_smith"}}
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 201
        mock_get.return_value = Mock()
        mock_get.return_value.json.return_value = {'username':'carlos'}
        mock_get.return_value.ok = True
        mock_get.return_value.status_code = 201
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(dict(
                    username='pedro',
                    password='123456'
                )),
                content_type='application/json'
            )
            r1 = self.client.get('/drivers/available')
            drivers = json.loads(r1.data.decode())
            data = json.loads(response.data.decode())
            auth_token = data['auth_token']
            response = self.client.patch(
                '/drivers',
                data=json.dumps(dict(
                    availability=True
                )),
                headers=dict(
                    Authorization='Bearer '+auth_token
                ),
                content_type='application/json'

                )
            response = self.client.patch(
                '/drivers',
                data=json.dumps(dict(
                    availability=False
                )),
                headers=dict(
                    Authorization='Bearer '+auth_token
                ),
                content_type='application/json'

                )
            data = json.loads(response.data.decode())
            response = self.client.get('/drivers/available')
            drivers = json.loads(response.data.decode())
            self.assertEqual(response.content_type,'application/json')
            self.assertEqual(response.status_code,200)
            self.assertTrue(isinstance(drivers,list))
            self.assertEqual(len(drivers), 0)


  
if __name__ == '__main__':
    unittest.main()
