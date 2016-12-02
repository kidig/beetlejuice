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


Errors = s.Object(
    errors=s.Array(s.String()),
)


UserDef = s.Definition('User', s.Object(
    id=s.Integer(),
    email=s.String(),
    first_name=s.String(),
    short_name=s.String(),
    avatar=s.Optional(s.String()),
))


class Signin(ApiView):
    '''
    User signin
    '''
    spec = Spec(
        Method.POST,
        s.Object(
            email=s.String(),
            password=s.String(),
        ),
        Response(200, schema=UserDef),
        Response(400, schema=Errors),
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

        return 400, {'errors': ['Email and/or password not recognized']}


class Logout(ApiView):
    '''
    User Logout
    '''
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
    User signup (Register)
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
        Response(301, description='user created, redirect to the next page'),
        Response(400, schema=Errors),
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
            return 400, {'errors': ['This email is already in use, please sign in']}


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
    '''
    Confirm user email
    '''
    spec = Spec(
        Method.GET,
        s.Query(
            id=s.Integer(),
            code=s.String(),
            next=s.Optional(s.String()),
        ),
        Response(301, description='redirect to the next page'),
    )

    def handle(self, data):
        code = data['code']
        user = User.objects.filter(pk=data['id']) \
            .exclude(email=None, new_email=None) \
            .filter(Q(email_confirm_code=code) | Q(new_email_confirm_code=code)) \
            .first()

        if user:
            if user.email_confirm_code == code:
                user.email_confirmed = True
                user.email_confirm_code = None
                user.is_active = True
                user.save(update_fields=['email_confirmed', 'email_confirm_code', 'is_active'])

                signals.email_confirmed.send(User, user=user)

                login(self.request, user)
                signals.signup_completed.send(User, user=user)

            elif user.new_email_confirm_code == code:
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(self.request, user)
                signals.signup_completed.send(User, user=user)

                if not User.objects.filter(email=user.new_email).exists():
                    user.email = user.new_email
                    user.new_email = None
                    user.new_email_confirm_code = None
                    user.email_confirmed = True
                    user.save(update_fields=['email', 'new_email', 'new_email_confirm_code', 'email_confirmed'])

        next = data['next'] or '/'

        return redirect(next)


class ResendEmailConfirm(ApiView):
    '''
    Re-send user email confirmation
    '''
    spec = Spec(
        Method.POST,
        s.Object(
            email=s.String()
        ),
        Response(202),
    )

    def handle(self, data):
        email = data['email'].lower()
        user = User.objects.filter(is_active=True).filter(Q(email=email) | Q(new_email=email)).first()
        if user:
            if (email == user.email and user.email_confirm_code):
                signals.user_email_confirm.send(User, user=user, email=email)

            if (email == user.new_email and user.new_email_confirm_code):
                signals.user_new_email_confirm.send(User, user=user, email=email)

        return 202


class ChangeEmail(ApiView):
    '''
    Change user email
    '''
    spec = Spec(
        Method.POST,
        s.Object(
            email=s.String(),
        ),
        Response(403, description='unauthorized access'),
        Response(400, schema=Errors),
        Response(200, schema=s.Object(
            email=s.String(),
        ))
    )

    def handle(self, data):
        user = getattr(self.request, 'user', None)
        if not (user or user.is_authenticated):
            return 403

        email = data['email'].lower()

        if User.objects.exclude(pk=user.pk).filter(Q(email=email) | Q(new_email=email)):
            return 400, {'errors': ['This email is already in use']}

        if user.email != email:
            user.email = email
            user.save(update_fields={'email'})

        if user.email == email:
            user.new_email = None
            user.new_email_confirm_code = None
        else:
            user.new_email = email
            user.new_email_confirm_code = random_key()

            signals.user_new_email_confirm.send(User, user=user, email=email)

        user.save(update_fields={'new_email', 'new_email_confirm_code'})

        return 200, {'email': user.email}


class ResetPassword(ApiView):
    '''
    Reset password confirmation
    '''
    spec = Spec(
        Method.POST,
        s.Object(
            email=s.String(),
        ),
        Response(202),
    )

    def handle(self, data):
        email = data['email'].lower()
        user = User.objects.filter(email=email, is_active=True).first()

        if user:
            user.password_reset_code = random_key()
            user.save(update_fields={'password_reset_code'})
            signals.password_reset.send(User, user=user)

        return 202


class SetPassword(ApiView):
    '''
    Set new user password
    '''
    spec = Spec(
        Method.POST,
        s.Object(
            id=s.Integer(),
            code=s.String(),
            password=s.String(),
        ),
        Response(200, schema=UserDef),
        Response(400, schema=Errors),
    )

    def handle(self, data):
        user = User.objects.filter(pk=data['id'], is_active=True, password_reset_code=data['code']).first()
        if not user:
            return 400, {'errors': ['Invalid password reset code']}

        user.set_password(data['password'])
        user.email_confirmed = True
        user.password_reset_code = None
        user.save(update_fields={'password', 'email_confirm', 'password_reset_code'})

        login(self.request, user)

        return 200, {
            'id': user.pk,
            'email': user.email,
            'first_name': user.first_name,
            'short_name': user.get_short_name(),
        }


class ChangePassword(ApiView):
    '''
    Change user password
    '''
    spec = Spec(
        Method.POST,
        s.Object(
            old_password=s.String(),
            new_password=s.String(),
        ),
        Response(403, description='unauthorized access'),
        Response(400, schema=Errors),
        Response(202),
    )

    def handle(self, data):
        user = getattr(self.request, 'user', None)
        if not (user or user.is_authenticated):
            return 403

        if not user.check_password(data['old_password']):
            return 400, {'errors': ['Wrong password']}

        user.set_password(data['new_password'])
        user.save(update_fields={'password'})

        return 202

