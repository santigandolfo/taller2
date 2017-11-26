import unittest
import json
import time
from src.models import User
from tests.base import BaseTestCase
from mock import patch, Mock
from app import application, TOKEN_DURATION


class TestRequestsSubmission(BaseTestCase):
    @patch('requests.post')
    def test_simple_request_submission(self, mock_post):
        """ Test case for a simple request succesfully submitted"""
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
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'request_submitted')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 201)

    @patch('requests.post')
    def test_request_submission_with_validation_transform(self, mock_post):
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
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'request_submitted')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 201)

    @patch('requests.post')
    def test_request_submission_missing_parameter(self, mock_post):
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

    @patch('requests.post')
    def test_request_submission_wrong_parameter(self, mock_post):
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

    @patch('requests.post')
    def test_request_submission_driver(self, mock_post):
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

    @patch('requests.post')
    def test_request_submission_unauthorized(self, mock_post):
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

    @patch('requests.post')
    def test_request_submission_missing_token(self, mock_post):
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

    @patch('requests.post')
    def test_request_submission_invalid_token(self, mock_post):
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

    @patch('requests.post')
    def test_request_submission_expired_token(self, mock_post):
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

    @patch('requests.post')
    def test_request_submission_with_pending_request(self, mock_post):
        """ Test case for a request submitted with an already pending request"""
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
            self.client.post(
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
            response = self.client.post(
                '/riders/pedro/request',
                data=json.dumps(dict(
                    latitude_initial=35.00,
                    latitude_final=21.32,
                    longitude_initial=-2.0,
                    longitude_final=-120.21
                )),
                headers=dict(
                    Authorization='Bearer ' + auth_token
                ),
                content_type='application/json'
            )

            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'one_request_already_pending')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 409)


class TestRequestDeletion(BaseTestCase):
    @patch('requests.post')
    def test_simple_request_deletion(self, mock_post):
        """ Test case for a simple request succesfully deleted"""
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
            self.client.post(
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
            response = self.client.delete(
                '/riders/pedro/request',
                headers=dict(
                    Authorization='Bearer ' + auth_token
                ),
                content_type='application/json'
            )

            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'request_cancelled')
            self.assertEqual(data['count'], 1)
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 200)

    @patch('requests.post')
    def test_delete_request_never_submitted(self, mock_post):
        """ Test case for deleting a request that was never submitted"""
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
            response = self.client.delete(
                '/riders/pedro/request',
                headers=dict(
                    Authorization='Bearer ' + auth_token
                ),
                content_type='application/json'
            )

            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'no_pending_request')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 404)

    @patch('requests.post')
    def test_delete_request_unauthorized(self, mock_post):
        """ Test case for deleting a request without corresponding authorization"""
        mock_post.return_value = Mock()
        mock_post.return_value.json.return_value = {'id': "1"}
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 201
        with self.client:
            self.client.post(
                '/users',
                data=json.dumps(dict(
                    username='juan',
                    password='123456',
                    type='passenger'
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
            response = self.client.delete(
                '/riders/juan/request',
                headers=dict(
                    Authorization='Bearer ' + auth_token
                ),
                content_type='application/json'
            )

            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'unauthorized_deletion')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 401)

    @patch('requests.post')
    def test_delete_request_missing_token(self, mock_post):
        """ Test case for deleting a request without a token"""
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
            response = self.client.delete(
                '/riders/pedro/request',
                content_type='application/json'
            )

            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'missing_token')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 401)

    @patch('requests.post')
    def test_delete_request_invalid_token(self, mock_post):
        """ Test case for deleting a request with an invalid token"""
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
            response = self.client.delete(
                '/riders/pedro/request',
                headers=dict(
                    Authorization='Bearer snajdsnajdaskdwe3414314123'
                ),
                content_type='application/json'
            )

            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'invalid_token')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 401)

    @patch('requests.post')
    def test_delete_request_expired_token(self, mock_post):
        """ Test case for deleting a request with an expired token"""
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
            response = self.client.delete(
                '/riders/pedro/request',
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


class TestIntegrationRequests(BaseTestCase):
    @patch('requests.post')
    def test_submit_request_cancel_submit_again(self, mock_post):
        """ Test case for a succesful submit after deleting a previous submit"""
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
            self.client.post(
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
            self.client.delete(
                '/riders/pedro/request',
                headers=dict(
                    Authorization='Bearer ' + auth_token
                ),
                content_type='application/json'
            )
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
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'request_submitted')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 201)


class TestAvailableRequests(BaseTestCase):
    @patch('requests.post')
    @patch('requests.get')
    def test_no_requests_availabe(self, mock_get, mock_post):
        """Test case for a driver asking for requests available and getting empty list"""
        mock_post.return_value = Mock()
        mock_post.return_value.json.return_value = {'id': "1"}
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 201
        mock_get.return_value = Mock()
        mock_get.return_value.json.return_value = {'username': 'carlos'}
        mock_get.return_value.ok = True
        mock_get.return_value.status_code = 200
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
            response = self.client.get('/requests/available',
                                       headers=dict(
                                           Authorization='Bearer ' + auth_token
                                       ),
                                       )
            requests = json.loads(response.data.decode())
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 200)
            self.assertTrue(isinstance(requests, list))
            self.assertEqual(len(requests), 0)

    @patch('requests.post')
    @patch('requests.get')
    def test_one_request_availabe(self, mock_get, mock_post):
        """Test case for a passenger creating a request and a driver asking for it succesfully"""
        mock_post.return_value = Mock()
        mock_post.return_value.json.return_value = {'id': "1"}
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 201
        mock_get.return_value = Mock()
        mock_get.return_value.json.return_value = {'username': 'carlos'}
        mock_get.return_value.ok = True
        mock_get.return_value.status_code = 200
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(dict(
                    username='juan',
                    password='123456',
                    type='passenger'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            auth_token2 = data['auth_token']
            self.client.post(
                '/riders/juan/request',
                data=json.dumps(dict(
                    latitude_initial=30.00,
                    latitude_final=31.32,
                    longitude_initial=42,
                    longitude_final=43.21
                )),
                headers=dict(
                    Authorization='Bearer ' + auth_token2
                ),
                content_type='application/json'
            )
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
            auth_token1 = data['auth_token']
            response = self.client.get('/requests/available',
                                       headers=dict(
                                           Authorization='Bearer ' + auth_token1
                                       ),
                                       )
            requests = json.loads(response.data.decode())
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 200)
            self.assertTrue(isinstance(requests, list))
            self.assertEqual(len(requests), 1)

    @patch('requests.post')
    def test_requests_available_unauthorized(self, mock_post):
        """ Test case for asking for requests available without proper authorization"""
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
                    type='passenger'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            auth_token = data['auth_token']
            response = self.client.get(
                '/requests/available',
                headers=dict(
                    Authorization='Bearer ' + auth_token
                ))
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'unauthorized_request')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 401)

    def test_requests_available_missing_token(self):
        """ Test case for asking for available requests without a token"""
        with self.client:
            response = self.client.get('/requests/available')
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'missing_token')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 401)

    def test_requests_available_invalid_token(self):
        """ Test case for asking for available requests with an invalid token"""
        with self.client:
            response = self.client.get(
                '/requests/available',
                headers=dict(
                    Authorization='Bearer a'
                ))
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'invalid_token')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 401)

    @patch('requests.post')
    def test_requests_available_expired_token(self, mock_post):
        """ Test case for asking for available requests with an expired token"""
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
            response = self.client.get(
                '/requests/available',
                headers=dict(
                    Authorization='Bearer ' + auth_token
                ))
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'expired_token')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    unittest.main()
