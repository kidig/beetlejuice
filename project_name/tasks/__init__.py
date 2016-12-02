import requests
from django.core.files.base import ContentFile
from easy_thumbnails.files import generate_all_aliases
from robust import task

from . import mail
from ..models import User


@task(bind=True, retries=3)
def upload_user_avatar(self, user_id: int):
    user = User.objects.get(pk=user_id)

    try:
        response = requests.get(user.avatar_url, stream=True)
        if response.status_code == 200:
            user.avatar_image.save(user.avatar_url, ContentFile(response.raw.read()))
            user.save(update_fields=['avatar_image'])

            generate_all_aliases(user.avatar_image, include_global=False)

    except requests.exceptions.Timeout:
        self.retry()


@task()
def generate_avatar_thumbnails(user_id):
    instance = User.objects.get(pk=user_id)
    generate_all_aliases(instance.avatar_image, include_global=False)
