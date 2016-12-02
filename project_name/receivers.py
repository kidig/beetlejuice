from typing import Optional

from django.conf import settings
from django.db import models
from django.dispatch import receiver

from . import signals, tasks, transaction
from .models import User


@receiver(signal=models.signals.post_save, sender=User)
def grant_admin_permissions(instance: User, **kwargs) -> None:
    if instance.email in settings.SUPERUSERS:
        if not instance.is_superuser or not instance.is_staff:
            instance.is_superuser = True
            instance.is_staff = True
            if not instance.has_usable_password():
                instance.set_password(settings.SUPERUSER_DEFAULT_PASSWORD)
            if 'update_fields' in kwargs:
                instance.save(update_fields=['is_superuser', 'is_staff', 'password'])


@receiver(signal=models.signals.post_save, sender=User)
def upload_user_avatar(instance: User, created: bool, **kwargs) -> None:
    if created:
        if instance.avatar_url:
            transaction.on_commit(tasks.upload_user_avatar.delay, user_id=instance.pk)


@receiver(signal=signals.user_avatar_updated, sender=User)
def generate_avatar_thumbs(user: User, **kwargs) -> None:
    tasks.generate_avatar_thumbnails.delay(user_id=user.pk)


@receiver(signal=signals.signup_completed, sender=User)
def send_user_signup_completed_email(user: User, **kwargs) -> None:
    transaction.on_commit(
        tasks.mail.mail_signup_completed.delay,
        user_id=user.pk)


@receiver(signal=signals.user_email_confirm)
def send_user_confirm_email(user: User, email: str, next: Optional[str] = None, **kwargs) -> None:
    transaction.on_commit(
        tasks.mail.mail_confirm_email.delay,
        user_id=user.pk,
        email=email,
        next=next)


@receiver(signal=signals.user_new_email_confirm)
def send_user_change_email(user: User, email: str, **kwargs) -> None:
    transaction.on_commit(tasks.mail.mail_updated_email.delay, user_id=user.pk)
    transaction.on_commit(tasks.mail.mail_change_email.delay, user_id=user.pk, email=email)


@receiver(signal=signals.password_reset)
def send_password_reset_email(user: User, **kwargs) -> None:
    transaction.on_commit(tasks.mail.mail_password_reset.delay, user_id=user.pk)
