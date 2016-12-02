import api.schema as s
from api.exceptions import RequestParseError
from api.spec import Spec, Response
from api.views import ApiView, Method
from api.router import Router
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.shortcuts import redirect

from . import signals
from .models import User
from .utils import random_key
import copy


router = Router(namespace='api')


NonFieldError = s.Object(
    non_field_errors=s.Array(s.String()),
)


UserDef = s.Definition('User', s.Object(
    id=s.Integer(),
    email=s.String(),
    first_name=s.String(),
    short_name=s.String(),
    avatar=s.Optional(s.String()),
))


class Signin(ApiView):
    spec = Spec(
        Method.POST,
        s.Object(
            email=s.String(),
            password=s.String(),
        ),
        Response(200, schema=UserDef),
        Response(400, schema=NonFieldError),
        Response(423),
    )

    def handle(self, data):
        user = authenticate(username=data['email'], password=data['password'])

        if user and user.is_active and user.email_confirmed:
            login(self.request, user)
            return {
                'id': user.pk,
                'email': user.email,
                'first_name': user.first_name,
                'short_name': user.get_short_name(),
            }

        if user and (not user.email_confirmed or not user.is_active):
            return 423

        return 400, {'non_field_errors': ['Email and/or password not recognized']}


class Logout(ApiView):
    spec = Spec(
        Method.POST,
        s.Empty,
        Response(204),
    )

    def handle(self, data):
        logout(self.request)
        return 204


class Signup(ApiView):
    '''
    Signup user
    '''
    spec = Spec(
        Method.POST,
        s.Object(
            email=s.String(),
            first_name=s.String(),
            last_name=s.String(),
            password=s.String(),
            next=s.Optional(s.String()),
        ),
        Response(202, description='user created, need to email confirmation'),
        Response(301, description='user created, redirect to next page'),
        Response(400, schema=NonFieldError),
    )

    def create_user(self, **kwargs):
        confirm_code = kwargs.pop('email_confirm_code', random_key())
        return User.objects.create_user(
            email_confirm_code=confirm_code,
            **kwargs,
        )

    def handle(self, data):
        data = copy.copy(data)
        next = data.pop('next', None)
        data['email'] = data['email'].lower()

        if User.objects.filter(Q(email=data['email']) | Q(new_email=data['email'])).exists():
            return 400, {'non_field_errors': ['This email is already in use, please sign in']}


        if settings.EMAIL_CONFIRMATION:
            user = self.create_user(**data)
            signals.user_email_confirm.send(User, user=user, email=user.email, next=next)
            return 202
        else:
            user = self.create_user(email_confirmed=True, **data)
            login(self.request, user)
            signals.signup_completed.send(User, user=user)
            return redirect(next or '/')


class EmailConfirm(ApiView):
    spec = Spec(
        Method.GET,
        s.Query(
            id=s.Integer(),
            code=s.String(),
            next=s.Optional(s.String()),
        ),
        Response(204),
    )

    def handle(self, data):
        return 204
