from __future__ import unicode_literals
import unittest

from flask import Flask
from flask.ext import restful
from notify.utils import crossdomain


class CORSTestCase(unittest.TestCase):

    def test_crossdomain(self):

        class Foo(restful.Resource):

            decorators = [
                crossdomain(origin='*')
            ]

            def get(self):
                return "data"

        app = Flask(__name__)
        api = restful.Api(app)
        api.add_resource(Foo, '/')

        with app.test_client() as client:
            res = client.get('/')

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers['Access-Control-Allow-Origin'], '*')
        self.assertEqual(res.headers['Access-Control-Max-Age'], '21600')
        self.assertIn('HEAD', res.headers['Access-Control-Allow-Methods'])
        self.assertIn('OPTIONS', res.headers['Access-Control-Allow-Methods'])
        self.assertIn('GET', res.headers['Access-Control-Allow-Methods'])

    def test_no_crossdomain(self):

        class Foo(restful.Resource):

            def get(self):
                return "data"

        app = Flask(__name__)
        api = restful.Api(app)
        api.add_resource(Foo, '/')

        with app.test_client() as client:
            res = client.get('/')

        self.assertEqual(res.status_code, 200)
        self.assertNotIn('Access-Control-Allow-Origin', res.headers)
        self.assertNotIn('Access-Control-Allow-Methods', res.headers)
        self.assertNotIn('Access-Control-Max-Age', res.headers)
