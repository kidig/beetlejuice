import random

import factory
import factory.django
import requests

from .test.utils import keep_plain_password

DEFAULT_EMAIL_DOMAIN = 'example.org'

DEFAULT_USER_PASSWORD = '123qwe123'


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'project_name.User'

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.LazyAttributeSequence(lambda o, n: '{}{}@{}'.format(
        o.first_name.lower(), n, DEFAULT_EMAIL_DOMAIN,
    ))
    password = DEFAULT_USER_PASSWORD

    @classmethod
    def get_random_avatar(cls):
        params = {
            'inc': 'picture',
            'gender': random.choice(['male', 'female']),
            'results': 1
        }
        response = requests.get('http://api.randomuser.me/', params)
        response.raise_for_status()
        data = response.json()
        return data['results'].pop()['picture']['large']

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        manager = cls._get_manager(model_class)

        avatar_random = kwargs.pop('avatar_random', False)
        if avatar_random:
            kwargs['avatar_url'] = cls.get_random_avatar()

        user = manager.create_user(*args, **kwargs)
        user._password = kwargs.get('password')
        user.save = keep_plain_password(user)
        return user
