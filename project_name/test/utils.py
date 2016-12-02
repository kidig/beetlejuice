import json
import os
import types
from functools import wraps

import pytest
from django.contrib.auth import get_user_model
from django.core.serializers.json import DjangoJSONEncoder
from django.test import override_settings, TestCase
from django.test.client import Client
from django.utils.http import urlencode
from happymailer.models import TemplateModel

from ..mails import DefaultLayout

API_BASE_PATH = '/api/'


User = get_user_model()

integration_test = pytest.mark.skipif(os.environ.get('NO_INTEGRATION', None) == '1', reason='skip integration test')
skip_ci_test = pytest.mark.skipif(os.environ.get('SKIP_CI_TEST', None) == '1', reason='skip ci test')

ignore_external = override_settings(
    FIREBASE_SKIP=True,
    STRIPE_SKIP=True,
    EMAIL_SKIP=True,
    ROBUST_ALWAYS_EAGER=True,
)


class JsonClient(Client):
    def _make_path(self, path):
        if not path.startswith('/api/'):
            return '{}{}'.format(API_BASE_PATH, path)
        return path

    def _json_request(self, method, path, data, secure=False, **extra):
        method = method.lower()
        assert method in {'delete', 'get', 'head', 'options', 'patch', 'post', 'put'}
        if data is not None:
            if method in {'patch', 'post', 'put'}:
                data_str = json.dumps(data, cls=DjangoJSONEncoder)
                extra = {'data': data_str, **extra}
            else:
                extra = {'QUERY_STRING': urlencode(data, doseq=True), **extra}
        response = self.generic(method, self._make_path(path), secure=secure,
                                content_type='application/json', **extra)
        return response

    def delete(self, path, data=None, secure=False, **extra):
        return self._json_request('delete', path, data, **extra)

    def get(self, path, data=None, secure=False, **extra):
        return self._json_request('get', path, data, **extra)

    def head(self, path, data=None, secure=False, **extra):
        return self._json_request('head', path, data, **extra)

    def options(self, path, data=None, secure=False, **extra):
        return self._json_request('options', path, data, **extra)

    def patch(self, path, data=None, secure=False, **extra):
        return self._json_request('patch', path, data, **extra)

    def post(self, path, data=None, secure=False, **extra):
        return self._json_request('post', path, data, **extra)

    def put(self, path, data=None, secure=False, upload=False, **extra):
        if upload:
            return self.generic('put', self._make_path(path), data=data, content_type=extra.pop('content_type'),
                                **extra)
        else:
            return self._json_request('put', path, data, **extra)


class APITestCase(TestCase):
    client_class = JsonClient

    def login(self, user):
        assert user._password is not None
        self.client.login(username=user.email, password=user._password)

    def force_login(self, user):
        self.client.force_login(user)

    def logout(self):
        self.client.logout()


def keep_plain_password(user):
    """
    Monkey patch user.save method so that
    user object will have attribute _password after calling user.save()
    """
    fn = user.save

    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        _password = self._password
        fn(*args, **kwargs)
        self._password = _password

    return types.MethodType(wrapper, user)


class CreateMailTemplateMixin:
    @staticmethod
    def create_mail_template(*template_classes, **kwargs):
        layout = kwargs.pop('layout', DefaultLayout)
        subject = kwargs.pop('subject', 'test')
        body = kwargs.pop('body', 'test')
        enabled = kwargs.pop('enabled', True)

        return [TemplateModel.objects.create(
            name=cls.name,
            layout=layout.name,
            subject=subject,
            body=body,
            enabled=enabled,
            **kwargs,
        ) for cls in template_classes]
