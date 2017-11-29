import unittest
import json
from tests.base import BaseTestCase
from mock import patch, Mock


class TestDriverDutyStatusManipulation(BaseTestCase):
    @patch('requests.post')
    def test_simple_data_update(self, mock_post):
        """ Test case for a simple duty status change"""
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
            response = self.client.patch(
                '/drivers/pedro',
                data=json.dumps(dict(
                    duty=True
                )),
                headers=dict(
                    Authorization='Bearer ' + auth_token
                ),
                content_type='application/json'

            )

            data = json.loads(response.data.decode())

            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'updated_duty_status')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 200)

    @patch('requests.post')
    @patch('requests.get')
    def test_one_driver_available(self, mock_get, mock_post):
        """Make a driver available, request of available drivers should display it"""
        mock_post.return_value = Mock()
        mock_post.return_value.json.return_value = {'id': "1"}
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 201
        mock_get.return_value = Mock()
        mock_get.return_value.json.return_value = {'username': 'carlos'}
        mock_get.return_value.ok = True
        mock_get.return_value.status_code = 201
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
            response = self.client.patch(
                '/drivers/pedro',
                data=json.dumps(dict(
                    duty=True
                )),
                headers=dict(
                    Authorization='Bearer ' + auth_token
                ),
                content_type='application/json'

            )
            response = self.client.get('/drivers/available')
            drivers = json.loads(response.data.decode())
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 200)
            self.assertTrue(isinstance(drivers, list))
            self.assertEqual(len(drivers), 1)
            self.assertEqual(drivers[0]['username'], 'carlos')

    @patch('requests.post')
    @patch('requests.get')
    def test_one_driver_not_availabe(self, mock_get, mock_post):
        """Make a driver available, then make it unavailable, request of available drivers should not display it"""
        mock_post.return_value = Mock()
        mock_post.return_value.json.return_value = {'id': "1"}
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 201
        mock_get.return_value = Mock()
        mock_get.return_value.json.return_value = {'username': 'carlos'}
        mock_get.return_value.ok = True
        mock_get.return_value.status_code = 201
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
            r1 = self.client.get('/drivers/available')
            json.loads(r1.data.decode())
            data = json.loads(response.data.decode())
            auth_token = data['auth_token']
            self.client.patch(
                '/drivers/pedro',
                data=json.dumps(dict(
                    duty=True
                )),
                headers=dict(
                    Authorization='Bearer ' + auth_token
                ),
                content_type='application/json'

            )
            self.client.patch(
                '/drivers/pedro',
                data=json.dumps(dict(
                    duty=False
                )),
                headers=dict(
                    Authorization='Bearer ' + auth_token
                ),
                content_type='application/json'

            )
            response = self.client.get('/drivers/available')
            drivers = json.loads(response.data.decode())
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 200)
            self.assertTrue(isinstance(drivers, list))
            self.assertEqual(len(drivers), 0)

    @patch('requests.post')
    def test_missing_duty_status(self, mock_post):
        """duty status is missing, error should  be received"""
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
            response = self.client.patch(
                '/drivers/pedro',
                data=json.dumps(dict(
                )),
                headers=dict(
                    Authorization='Bearer ' + auth_token
                ),
                content_type='application/json'

            )

            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'missing_duty_status')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 400)

    @patch('requests.post')
    def test_change_duty_status_unexisting_user(self, mock_post):
        """Change duty status of an unexisting user, error should  be received"""
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
            response = self.client.patch(
                '/drivers/juan',
                data=json.dumps(dict(
                    duty=True
                )),
                headers=dict(
                    Authorization='Bearer ' + auth_token
                ),
                content_type='application/json'

            )

            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'driver_not_found')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 404)

    @patch('requests.post')
    def test_change_duty_status_of_another_user(self, mock_post):
        """Try to change the duty status of another user"""
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
                    type='driver'
                )),
                content_type='application/json'
            )
            response = self.client.post(
                '/users',
                data=json.dumps(dict(
                    username='juan',
                    password='123456',
                    type='driver'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            auth_token = data['auth_token']
            response = self.client.patch(
                '/drivers/pedro',
                data=json.dumps(dict(
                    duty=True
                )),
                headers=dict(
                    Authorization='Bearer ' + auth_token
                ),
                content_type='application/json'

            )

            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'unauthorized_update')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 401)


    @patch('requests.post')
    def test_change_duty_status_without_token(self, mock_post):
        """Change duty status without a token, error should  be received"""
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
                    type='driver'
                )),
                content_type='application/json'
            )
            response = self.client.patch(
                '/drivers/pedro',
                data=json.dumps(dict(
                    duty=True
                )),
                headers=dict(
                ),
                content_type='application/json'

            )

            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'missing_token')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    unittest.main()
