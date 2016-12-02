import logging
import os

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.gis.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from easy_thumbnails.alias import aliases
from easy_thumbnails.fields import ThumbnailerImageField
from easy_thumbnails.namers import source_hashed

from .utils import capname, random_key

logger = logging.getLogger(__name__)


class UserQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)


class UserManager(BaseUserManager):
    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)

    def create_user(self, email, first_name, last_name, password=None, **kwargs):
        if not email:
            raise ValueError('Users must have an email')

        user = User(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            date_joined=timezone.now(),
            **kwargs,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **kwargs):
        if not email:
            raise ValueError('Users must have an email')

        user = User(
            email=self.normalize_email(email),
            is_staff=True,
            is_superuser=True,
            date_joined=timezone.now(),
            **kwargs,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    new_email = models.EmailField(blank=True, null=True, db_index=True)
    email_confirm_code = models.TextField(blank=True, null=True)
    new_email_confirm_code = models.TextField(blank=True, null=True)
    email_confirmed = models.BooleanField(default=False)
    password_reset_code = models.TextField(blank=True, null=True)

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    def avatar_image_path(self, filename):
        extension = os.path.splitext(filename)[1][1:]
        return 'user_avatars/{}/{}'.format(self.pk, random_key(4), source_hashed(random_key(4), ['orig'], extension))

    avatar_url = models.TextField(blank=True, null=True)
    avatar_image = ThumbnailerImageField(
        upload_to=avatar_image_path,
        resize_source={'size': (300, 300), 'crop': True},
        blank=True,
        null=True,
    )

    @cached_property
    def avatar(self):
        if not self.avatar_image:
            if self.avatar_url:
                return {key: self.avatar_url for key in settings.THUMBNAIL_ALIASES['project_name.User.avatar_image']}
            return None

        all_options = aliases.all(self.avatar_image)
        return {key: self.avatar_image[key].url for key in all_options.keys()}

    ip_address = models.GenericIPAddressField(blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def _get_name(self, short=False):
        if not self.first_name:
            return self.email
        first_name = capname(self.first_name)
        if self.last_name:
            last_name = capname(self.last_name)
            if short:
                last_name = '{}.'.format(last_name[0])
            return '{} {}'.format(first_name, last_name)

        return first_name

    def get_full_name(self):
        return self._get_name(short=False)

    def get_short_name(self):
        return self._get_name(short=True)

    @property
    def email_recipient(self):
        return '{} {} <{}>'.format(self.first_name, self.last_name, self.email)

    @property
    def new_email_recipient(self):
        return '{} {} <{}>'.format(self.first_name, self.last_name, self.new_email)

    def __str__(self):
        return '{} (ID: {})'.format(self.get_full_name(), self.id)
