from __future__ import unicode_literals
import os

import flask.config

from flask.ext import restful
from flask.ext.mongoengine import MongoEngine

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


config = flask.config.Config(cwd, flask.Flask.default_config)
config.from_object(app_name + '.settings')
config.from_pyfile('settings.cfg', silent=True)
if os.getenv(app_name.upper() + '_ENV'):
    env = os.getenv(app_name.upper() + '_ENV')
    config.from_object(app_name + '.settings.' + env)


db = MongoEngine()
api = restful.Api()


def make_app():
    import factory

    application = factory.create_app(app_name, cwd, settings_override=config)
    db.init_app(application)
    api.init_app(application)
    factory.register_resources(api, app_name, cwd)

    return application


if __name__ == '__main__':
    app = make_app()
    app.run()