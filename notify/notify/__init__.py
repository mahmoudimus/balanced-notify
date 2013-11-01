from __future__ import unicode_literals
import os

from flask.ext import restful
from flask.ext.mongoengine import MongoEngine

import factory


__version__ = 1

cwd = os.path.dirname(os.path.realpath(__file__))
version_file = os.path.join(cwd, '_version')
app_name = 'notify'


try:
    f = open(version_file, 'r').read()
    __version__ = f.strip()
except IOError:
    # Not present locally
    pass


app = factory.create_app(app_name, cwd)
config = app.config
db = MongoEngine(app)
api = restful.Api(app)


def make_app():
    factory.register_blueprints(app, app_name, [cwd])
    factory.register_resources(api, app_name, cwd)

    return app


if __name__ == '__main__':
    app = make_app()
    app.run()