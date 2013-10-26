import os

from flask.ext.mongoengine import MongoEngine

import app


app = app.create_app(__name__, os.path.abspath(os.path.dirname(__file__)))
db = MongoEngine(app)


if __name__ == '__main__':
    app.run()