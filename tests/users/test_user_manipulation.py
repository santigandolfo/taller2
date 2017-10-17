import unittest
import json
import time
from src.models import User
from tests.base import BaseTestCase
from mock import patch,Mock
from app import application, TOKEN_DURATION

class TestBasic(BaseTestCase):

    @patch('requests.post')
    @patch('requests.put')
    def test_simple_data_update(self, mock_put,mock_post):
        """ Test case for a simple data update"""
        mock_post.return_value = Mock()
        mock_post.return_value.json.return_value = {'status':'success','message':'user_registered','auth_token':'fmsdakfkldskafl.fdsalfkdsa.fdsafsd', "user":{"username":"joe_smith"}}
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 201
        mock_put.return_value = Mock()
        mock_put.return_value.json.return_value = {'status':'success','message':'data_changed','auth_token':'fmsdakfkldskafl.fdsalfkdsa.fdsafsd', "user":{"username":"joe_smith"}}
        mock_put.return_value.ok = True
        mock_put.return_value.status_code = 200
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
            auth_token = data['auth_token']
            response = self.client.put(
                '/users',
                data=json.dumps(dict(
                    data=1
                )),
                headers=dict(
                    Authorization='Bearer '+auth_token
                ),
                content_type='application/json'

                )

            data = json.loads(response.data.decode())
            self.assertEqual(data['status'],'success')
            self.assertEqual(data['message'],'data_changed_succesfully')
            self.assertEqual(response.content_type,'application/json')
            self.assertEqual(response.status_code,200)

    def test_simple_invalid_data_update(self):
        """ Test case for a failing data update"""
        
        with self.client:
            auth_token = ''
            with patch('requests.post') as mock_post:
                mock_post.return_value = Mock()
                mock_post.return_value.json.return_value = {'status':'success','message':'user_registered','auth_token':'fmsdakfkldskafl.fdsalfkdsa.fdsafsd', "user":{"username":"joe_smith"}}
                mock_post.return_value.ok = True
                mock_post.return_value.status_code = 201
                response = self.client.post(
                    '/users',
                    data=json.dumps(dict(
                        username='joe_smith',
                        password='123456'
                    )),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                auth_token = data['auth_token']
            with patch('requests.put') as mock_put:
                mock_put.return_value = Mock()
                mock_put.return_value.json.return_value = {'status':'fail','message':'invalid_key','auth_token':'fmsdakfkldskafl.fdsalfkdsa.fdsafsd', "user":{"username":"joe_smith"}}
                mock_put.return_value.ok = False
                mock_put.return_value.status_code = 400
                response = self.client.put(
                    '/users',
                    data=json.dumps(dict(
                        data=1
                    )),
                    headers=dict(
                        Authorization='Bearer '+auth_token
                    ),
                    content_type='application/json'

                    )

                data = json.loads(response.data.decode())
                self.assertEqual(data['status'],'fail')
                self.assertEqual(data['message'],'invalid_key')
                self.assertEqual(response.content_type,'application/json')
                self.assertEqual(response.status_code,400)

    def test_data_update_missing_token(self):
        """ Test case for a failing data update because missing token"""
        
        with self.client:
            auth_token = ''
            with patch('requests.post') as mock_post:
                mock_post.return_value = Mock()
                mock_post.return_value.json.return_value = {'status':'success','message':'user_registered','auth_token':'fmsdakfkldskafl.fdsalfkdsa.fdsafsd', "user":{"username":"joe_smith"}}
                mock_post.return_value.ok = True
                mock_post.return_value.status_code = 201
                response = self.client.post(
                    '/users',
                    data=json.dumps(dict(
                        username='joe_smith',
                        password='123456'
                    )),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                auth_token = data['auth_token']
            with patch('requests.put') as mock_put:
                response = self.client.put(
                    '/users',
                    data=json.dumps(dict(
                        data=1
                    )),
                    content_type='application/json'

                    )

                data = json.loads(response.data.decode())
                self.assertEqual(data['status'],'fail')
                self.assertEqual(data['message'],'missing_token')
                self.assertEqual(response.content_type,'application/json')
                self.assertEqual(response.status_code,401)


    def test_data_update_with_expired_token(self):
        """ Test case for a failing data update because of expired token"""
        
        with self.client:
            auth_token = ''
            with patch('requests.post') as mock_post:
                mock_post.return_value = Mock()
                mock_post.return_value.json.return_value = {'status':'success','message':'user_registered','auth_token':'fmsdakfkldskafl.fdsalfkdsa.fdsafsd', "user":{"username":"joe_smith"}}
                mock_post.return_value.ok = True
                mock_post.return_value.status_code = 201
                response = self.client.post(
                    '/users',
                    data=json.dumps(dict(
                        username='joe_smith',
                        password='123456'
                    )),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                auth_token = data['auth_token']
            time.sleep(TOKEN_DURATION+1)
            with patch('requests.put') as mock_put:
                response = self.client.put(
                    '/users',
                    data=json.dumps(dict(
                        data=1
                    )),
                    headers=dict(
                        Authorization='Bearer '+auth_token
                    ),
                    content_type='application/json'

                    )

                data = json.loads(response.data.decode())
                self.assertEqual(data['status'],'fail')
                self.assertEqual(data['message'],'expired_token')
                self.assertEqual(response.content_type,'application/json')
                self.assertEqual(response.status_code,401)

    def test_data_update_with_invalid_token(self):
        """ Test case for a failing data update because of invalid token"""
        
        with self.client:
            
            with patch('requests.put') as mock_put:
                response = self.client.put(
                    '/users',
                    data=json.dumps(dict(
                        data=1
                    )),
                    headers=dict(
                        Authorization='Bearer kfdslfdajsfds.jfjdsalkjfasdjk.fdsajfskd'
                    ),
                    content_type='application/json'

                    )

                data = json.loads(response.data.decode())
                self.assertEqual(data['status'],'fail')
                self.assertEqual(data['message'],'invalid_token')
                self.assertEqual(response.content_type,'application/json')
                self.assertEqual(response.status_code,401)


  
if __name__ == '__main__':
    unittest.main()
