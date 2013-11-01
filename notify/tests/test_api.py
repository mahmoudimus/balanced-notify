import unittest

from flask import url_for
import simplejson as json
from jsonschema import validate

import notify
from notify.models import Notification, User


GET_NO_NOTIFICATIONS_SCHEMA = {
    "type": "object",
    "properties": {
        "data": {
            "type": "array",
            "maxItems": 0
        }
    },
    "required": ["data"]
}

NOTIFICATION_RESOURCE_SCHEMA = {
    "type": "object",
    "properties": {
        "data": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "id": {"type": "string"},
                    "href": {'type': 'string'},
                    'user': {'type': 'string'}
                },
                "additionalProperties": False,
            },
            "minItems": 1,
            "uniqueItems": True
        }
    },
    "additionalProperties": False,
}

GET_USERS_SCHEMA = {
    "type": "object",
    "properties": {
        "data": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "email": {"type": "string"},
                    "id": {"type": "string"}
                },
                "required": ["id", "email"]
            },
            "minItems": 1,
            "uniqueItems": True
        }
    },
    "required": ["data"]
}


class TestCase(unittest.TestCase):

    def setUp(self):
        app = notify.make_app()
        self.client = app.test_client()
        self.user_ids = {}
        for fixture in [
            {'email': 'app@balancedpayments.com'},
            {'email': 'tests@balancedpayments.com'}
        ]:
            identifier, _, _ = fixture['email'].partition('@')
            _user = User(**fixture).save()
            self.user_ids[identifier] = _user

    def tearDown(self):
        Notification.objects.delete()
        User.objects.delete()

    @property
    def app_user_id(self):
        return self.user_ids['app'].id

    @property
    def tests_user_id(self):
        return self.user_ids['tests'].id

    def assertStatus(self, response, status_code):
        """
        Helper method to check matching response status.

        :param response: Flask response
        :param status_code: response status code (e.g. 200)
        """
        self.assertEqual(response.status_code, status_code)

    def validateResponse(self, response, json_schema):
        """
        Helper method to parse a response as json and validate it given a
        json_schema

        :param response: Flask response
        :param json_schema: a json schema
        """

        data = json.loads(response.data)
        validate(data, json_schema)

        return data

    @property
    def notification_payload(self):
        return dict(
            message='Checkout this cool new feature on the Balanced dashboard',
            user=self.tests_user_id,
        )

    def test_create_notification(self):
        res = self.client.post(
            '/notifications',
            data=self.notification_payload,
            headers={'x-balanced-admin': '1'})

        data = self.validateResponse(res, NOTIFICATION_RESOURCE_SCHEMA)
        self.assertStatus(res, 201)

        return data['data']

    def test_create_notification_unauthorized(self):
        res = self.client.post(
            '/notifications',
            data=self.notification_payload)

        self.assertStatus(res, 401)

    def test_create_notification_not_admin_authorized(self):
        res = self.client.post(
            '/notifications',
            data=self.notification_payload,
            headers={'x-balanced-user': self.app_user_id})

        self.assertStatus(res, 401)

    def test_create_multi_notification(self):
        self.notification_payload.pop('uid', None)
        res = self.client.post(
            '/notifications',
            data=self.notification_payload,
            headers={'x-balanced-admin': '1'})
        print res.data
        data = self.validateResponse(res, NOTIFICATION_RESOURCE_SCHEMA)
        self.assertStatus(res, 201)

        return data['data']

    def test_get_notifications(self):
        notification_id = self.test_create_notification()
        res = self.client.get(
            '/notifications',
            headers={'x-balanced-user': self.app_user_id})

        data = self.validateResponse(res, NOTIFICATION_RESOURCE_SCHEMA)
        self.assertEqual(notification_id, data['data'][0]['id'])
        self.assertEqual(
            self.notification_payload.get('message'),
            data['data'][0]['message'])

        self.assertStatus(res, 200)

    def test_get_notifications_unauthorized(self):
        notification_id = self.test_create_notification()
        res = self.client.get(
            '/notifications')

        self.assertStatus(res, 401)

    def test_delete_notifications(self):
        notification_id = self.test_create_notification()
        res = self.client.delete(
            '/notifications/' + notification_id,
            headers={'x-balanced-user': self.app_user_id})

        self.assertStatus(res, 204)
        self.test_get_no_notifications()

    def test_delete_notifications_twice(self):
        notification_id = self.test_create_notification()
        for expected_status_code in (204, 403):
            resp = self.client.delete(
                '/notifications/' + notification_id,
                headers={'x-balanced-user': self.app_user_id})

            self.assertStatus(resp, expected_status_code)

    def test_delete_notifications_unauthorized(self):
        notification_id = self.test_create_notification()
        res = self.client.delete(
            '/notifications/' + notification_id)

        self.assertStatus(res, 401)

    def test_delete_notifications_another_user(self):
        notification_id = self.test_create_notification()
        res = self.client.delete(
            '/notifications/' + notification_id,
            headers={'x-balanced-user': '5'})

        self.assertStatus(res, 403)

    def test_delete_notifications_random_id(self):
        res = self.client.delete(
            '/notifications/1dnnn',
            headers={'x-balanced-user': '5'})

        self.assertStatus(res, 403)

    def test_get_no_notifications(self):
        res = self.client.get(
            '/notifications', headers={'x-balanced-user': self.app_user_id})

        self.assertIn('[]', res.data)

        self.validateResponse(res, GET_NO_NOTIFICATIONS_SCHEMA)
        self.assertStatus(res, 200)

    def test_get_users(self):
        res = self.client.get(
            '/users', headers={'x-balanced-admin': '1'})

        data = json.loads(res.data)
        self.validateResponse(res, GET_USERS_SCHEMA)

        self.assertGreaterEqual(len(data['data']), 1)
        self.assertStatus(res, 200)

    def test_get_users_unauthorized(self):
        res = self.client.get(
            '/users')

        self.assertStatus(res, 401)

    def test_get_users_not_admin_authorized(self):
        res = self.client.get(
            '/users', headers={'x-balanced-user': '1'})

        self.assertStatus(res, 401)


if __name__ == '__main__':
    unittest.main()
