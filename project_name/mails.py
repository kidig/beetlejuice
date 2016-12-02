import logging
import urllib.parse

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models import Q
from happymailer import Template, Layout, t
from happymailer.fake import fake

from .models import User

logger = logging.getLogger(__name__)


STATIC_URL = settings.STATIC_URL
if STATIC_URL.startswith('/'):
    STATIC_URL = 'https://{}{}'.format(settings.DOMAIN, STATIC_URL)


class TemplateException(Exception):
    pass


class DefaultLayout(Layout):
    name = 'project_name'
    description = 'Default Layout'
    content = '''
<mjml>
  <mj-body>
    <mj-container>
      <mj-section>
        <mj-column>
          <mj-text>{SITE_NAME}</mj-text>
        </mj-column>
      </mj-section>

      <mj-section>
        <mj-column>
          {{{{ body }}}}
        </mj-column>
      </mj-section>

      <mj-section>
        <mj-column>
          <mj-text>Sincerely, <br/>{SITE_NAME} Team</mj-text>
        </mj-column>
      </mj-section>
    </mj-container>
  </mj-body>
</mjml>
    '''.format(STATIC_URL=STATIC_URL, DOMAIN=settings.DOMAIN, SITE_NAME=name.capitalize())


def fake_user():
    first_name = fake.first_name()
    return {
        'first_name': first_name,
        'short_name': '{} {}'.format(first_name, fake.last_name()[0])
    }


def fake_internal_url():
    return 'https://{}/{}'.format(settings.DOMAIN, fake.uri_path())


class BaseTemplate(Template):
    abstract = True

    def post_init(self):
        raise NotImplementedError()


class UserMixin:
    user_variables = {
        'first_name': t.String(),
        'short_name': t.String(),
    }

    def get_user_variables(self, user=None):
        if user is None:
            user = self.user

        return {
            'first_name': user.first_name,
            'short_name': user.get_short_name(),
        }


class BaseUserTemplate(BaseTemplate, UserMixin):
    abstract = True

    kwargs = {
        'user_id': t.Int(),
    }

    variables = {
        'user': t.Dict(UserMixin.user_variables),
    }

    def post_init(self):
        self.user = User.objects.get(pk=self.kwargs['user_id'])
        self.add_recipient(self.user.email_recipient)

    def get_variables(self):
        return {
            'user': self.get_user_variables(),
        }

    @classmethod
    def fake_variables(cls):
        return {
            'user': fake_user(),
        }


class EmailConfirmTemplate(BaseUserTemplate):
    abstract = True

    kwargs = {
        'user_id': t.Int(),
        'email': t.String(),
        'next': t.Or(t.String(), t.Null()),
    }

    variables = {
        'button_link': t.URL(),
    }

    def post_init(self):
        email = self.kwargs['email']
        user = User.objects.filter(pk=self.kwargs['user_id']).filter(Q(email=email) |
                                                                     Q(new_email=email)).first()

        if user is None:
            raise TemplateException('No user found')
        self.user = user

        self.next = self.kwargs.get('next')

        self.confirm_code = None
        if user.email == email:
            recipient = user.email_recipient
            self.confirm_code = user.email_confirm_code
        elif user.new_email == email:
            recipient = user.new_email_recipient
            self.confirm_code = user.new_email_confirm_code
        else:
            raise TemplateException('Unknown email')

        self.add_recipient(recipient)

    def get_variables(self):
        variables = super(EmailConfirmTemplate, self).get_variables()
        query = {
            'id': self.user.pk,
            'code': self.confirm_code,
        }
        if self.next:
            query['next'] = self.next
        query = urllib.parse.urlencode(query)
        url = urllib.parse.urlunparse(('https', settings.DOMAIN, reverse('api:email_confirm'), '', query, ''))
        variables.update({'button_link': url})
        return variables

    @classmethod
    def fake_variables(cls):
        faked = super(EmailConfirmTemplate, cls).fake_variables()
        faked['button_link'] = fake_internal_url()
        return faked


# Templates
class SignupCompleted(BaseUserTemplate):
    name = 'signup_completed'


class EmailUpdated(BaseUserTemplate):
    name = 'email_updated'


class EmailChange(EmailConfirmTemplate):
    name = 'email_change'


class EmailConfirm(EmailConfirmTemplate):
    name = 'email_confirm'


class PasswordReset(BaseUserTemplate):
    name = 'password_reset'

    variables = {
        'button_link': t.URL(),
    }

    def post_init(self):
        user = User.objects.filter(pk=self.kwargs['user_id'],
                                   is_active=True).filter()
        if not user or not user.password_reset_code:
            raise TemplateException('No user found')
        self.user = user

        self.add_recipient(self.user.email_recipient)

    def get_variables(self):
        variables = super(PasswordReset, self).get_variables()
        query = urllib.parse.urlencode(
            {'id': self.user.pk, 'code': self.user.password_reset_code})
        url = urllib.parse.urlunparse(
            ('https', settings.DOMAIN, '/password_reset/', '', query, ''))
        variables.update({'button_link': url})
        return variables

    @classmethod
    def fake_variables(cls):
        faked = super(PasswordReset, cls).fake_variables()
        faked['button_link'] = fake_internal_url()
        return faked
