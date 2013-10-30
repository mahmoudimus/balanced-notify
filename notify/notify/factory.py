import importlib
import inspect

import pkgutil
from flask import Flask, Blueprint

from notify.resources import RegistrationMixin


def register_blueprints(app, package_name, package_path):
    """Register all Blueprint instances on the specified Flask application
    found in all modules for the specified package.

    :param app: the Flask application
    :param package_name: the package name
    :param package_path: the package path

    """
    rv = []
    for _, name, _ in pkgutil.iter_modules(package_path):
        m = importlib.import_module('%s.%s' % (package_name, name))
        for item in dir(m):
            item = getattr(m, item)
            if isinstance(item, Blueprint):
                app.register_blueprint(item)
            rv.append(item)
    return rv


def register_resources(api, package_name, package_path):
    """Register all Resource instances on the specified Flask-RESTful api
    instance for all Resource(s) found in all modules for the specified
    package.

    :param app: the Flask-RESTful application
    :param package_name: the package name
    :param package_path: the package path

    """
    if not isinstance(package_path, (list, tuple)):
        package_path = [package_path]

    rv = []
    for _, name, _ in pkgutil.iter_modules(package_path):
        m = importlib.import_module('%s.%s' % (package_name, name))
        for item in dir(m):
            item = getattr(m, item)

            if not inspect.isclass(item):
                continue
            if not issubclass(item, RegistrationMixin):
                continue
            if item is RegistrationMixin:
                continue

            item.register(api)
            rv.append(item)
    return rv


def create_app(package_name, package_path, settings_override=None):
    """Returns a :class:`Flask` application instance configured with common
    functionality.

    :param package_name: application package name
    :param package_path: application package path
    :param settings_override: a dictionary of settings to override

    """
    app = Flask(package_name, instance_relative_config=True)

    app.config.from_object('notify.settings')
    app.config.from_pyfile('settings.cfg', silent=True)
    app.config.from_object(settings_override)

    register_blueprints(app, package_name, [package_path])

    return app
