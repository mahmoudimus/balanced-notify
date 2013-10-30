from bson import json_util
from flask import request, Blueprint, make_response
from flask.ext.mongoengine.wtf import model_form
from flask.ext.restful import Resource, fields, marshal_with, marshal
from flask.views import MethodView
import simplejson as json

from notify import utils
from notify import auth
from notify import config
from notify import models
from notify import api

notification_fields = {
    'id': fields.String,
    'message': fields.String
}


@api.representation('application/json')
def as_json(data, code, headers=None):
    resp = make_response(json.dumps(data), code)
    resp.headers.extend(headers or {})
    return resp


class RegistrationMixin(object):

    url = None
    endpoint = None

    @classmethod
    def register(cls, resource_registry):
        resource_registry.add_resource(cls, cls.url, endpoint=cls.endpoint)


class Notifications(Resource, RegistrationMixin):

    url = '/notifications/<string:pk>'

    method_decorators = [
        utils.crossdomain(origin=config.get('CORS_DOMAIN')),
    ]

    @auth.user()
    @marshal_with(notification_fields)
    def get(self, pk):
        return models.Notification.objects.get_or_404(pk=pk)

    def delete(self, pk):
        notif = models.Notification.objects.get_or_404(pk=pk)
        notif.delete()
        return '', 204

    @auth.user()
    @marshal_with(notification_fields)
    def put(self, pk):
        notif = models.Notification.objects.get_or_404(pk=pk)
        return notif, 201


class NotificationsList(Resource, RegistrationMixin):

    url = '/notifications'

    method_decorators = [
        utils.crossdomain(origin=config.get('CORS_DOMAIN')),
    ]

    @marshal_with(notification_fields)
    def get(self):
        models.Notification.objects.all()

    def post(self):
        form_cls = model_form(models.Notification)
        notification = models.Notification()
        form = form_cls(request.form, csrf_enabled=False)
        if not form.validate():
            return json.dumps(form.errors, default=json_util.default), 400

        form.populate_obj(notification)
        notification.save()
        marshalled = marshal(notification, notification_fields)
        return marshalled, 201


user_fields = {
    'id': fields.String,
    'email': fields.String
}


class Users(Resource, RegistrationMixin):

    url = '/users/<string:pk>'

    method_decorators = [
        utils.crossdomain(origin=config.get('CORS_DOMAIN')),
        auth.admin()
    ]

    @marshal_with(user_fields)
    def get(self, pk):
        models.User.objects.get_or_404(pk=pk)


class UsersList(Resource, RegistrationMixin):

    url = '/users'

    method_decorators = [
        utils.crossdomain(origin=config.get('CORS_DOMAIN')),
        auth.admin()
    ]

    @marshal_with(user_fields)
    def get(self):
        return models.User.objects.all()


#class NotificationView(Resource):
#
#    decorators = [
#        utils.crossdomain(origin=config.get('CORS_DOMAIN')),
#    ]
#
#    @auth.user()
#    def get(self, id_):
#        if id_ is None:
#            self._index()
#        else:
#            self._show(id_)
#
#    def _index(self):
#        user_pk = request.headers.get('x-balanced-user')
#        user = User.objects.get(user_pk)
#        data = []
#        for notification in user.notifications:
#            data.append({
#                'message': notification.message,
#                'id': notification.id,
#            })
#        return json.dumps(data, default=json_util.default), 200
#
#    def _show(self, id_):
#        notification = Notification.objects.get(id_)
#        data = [dict(message=notification.message, id=notification.id)]
#        return json.dumps(data, default=json_util.default), 200
#
#    def post(self):
#        form_cls = model_form(Notification)
#        notification = Notification()
#        form = form_cls(request.form, csrf_enabled=False)
#        if not form.validate():
#            return json.dumps(form.errors, default=json_util.default), 400
#
#        form.populate_obj(notification)
#        notification.save()
#        data = [dict(message=notification.message, id='%s' % notification.pk)]
#        return json.dumps({'data': data}, default=json_util.default), 201
#
#    @auth.user()
#    def delete(self, notification_id):
#        notification = Notification.objects.get_or_404(pk=notification_id)
#        notification.delete()
#        return '', 204
#
#
#notifications = Blueprint('notifications', __name__,
#                          url_prefix='/notifications')
#utils.register_api(
#    view=NotificationView,
#    endpoint='notifications',
#    url='',
#    app=notifications,
#    pk='notification_id',
#    pk_type='string'
#)


#class UsersView(MethodView):
#
#    decorators = [
#        utils.crossdomain(origin=config.get('CORS_DOMAIN')),
#        auth.admin()
#    ]
#
#    def get(self, id_=None):
#        if id_ is None:
#            self._index()
#        else:
#            self._show(id_)
#
#    def _index(self):
#        data = []
#        for user in User.objects.all():
#            data.append({
#                'id': user.id,
#                'email': user.email,
#            })
#        return json.dumps({'data': data}, default=json_util.default), 200
#
#
#    def _show(self, id_):
#        user = User.objects.get(pk=id_)
#        data = [dict(id=user.id, email=user.email)]
#        return json.dumps({'data': data}, default=json_util.default), 200
#
#
#users = Blueprint('users', __name__, url_prefix='/users')
#utils.register_api(
#    view=UsersView,
#    endpoint='users',
#    url='',
#    app=users,
#    pk='user_id',
#    pk_type='string'
#)


#@app.route('/notifications', methods=['GET'])
#@crossdomain(origin=app.config.get('CORS_DOMAIN'))
#@auth.user()
#def get_notifications():
#    user = request.headers.get('x-balanced-user')
#    notification_cursor = Notification.get_for_user(user)
#
#    return (
#        json.dumps({'data': [{'message': doc['message'], 'id': str(doc['_id'])}
#                   for doc in notification_cursor]}, default=json_util.default)
#    ), 200
#
#
#@app.route('/notification', methods=['POST'])
#@crossdomain(origin=app.config.get('CORS_DOMAIN'))
#@auth.admin()
#def create_notifications():
#    if not request.form['message']:
#        return 'Message required', 400
#
#    message = str(request.form['message'])
#    user_id = request.form.get('uid')
#
#    notification_id = Notification.create_notifications(message, user_id)
#
#    return (
#        json.dumps(
#            {'data': str(notification_id) if isinstance(notification_id,
#                                                        ObjectId) else [str(
#                obj_id) for obj_id in notification_id]},
#            default=json_util.default)
#    ), 201
#
#
#@app.route('/notification/<string:notification_id>', methods=['DELETE'])
#@crossdomain(origin=app.config.get('CORS_DOMAIN'))
#@auth.user()
#def mark_notification_as_read(notification_id):
#    user = request.headers.get('x-balanced-user')
#    res = Notification.delete_notification(user, notification_id)
#
#    if res['n'] >= 1:
#        return '', 204
#    else:
#        return 'Forbidden', 403
#
#
#@app.route('/users', methods=['GET'])
#@crossdomain(origin=app.config.get('CORS_DOMAIN'))
#@auth.admin()
#def get_all_users():
#    return (
#        json.dumps({'data': [{'id': str(doc['_id']), 'email': doc['email']}
#                   for doc in User.get_users()]}, default=json_util.default)
#    ), 200
