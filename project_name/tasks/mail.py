from robust import task

from ..mails import EmailConfirm, EmailChange, EmailUpdated, PasswordReset, SignupCompleted


__all__ = ['mail_signup_completed', 'mail_confirm_email', 'mail_change_email',
           'mail_updated_email', 'mail_password_reset']


@task()
def mail_signup_completed(user_id):
    return SignupCompleted(user_id=user_id).send()


@task()
def mail_confirm_email(user_id, email, next=None):
    return EmailConfirm(user_id=user_id, email=email, next=next).send()


@task()
def mail_change_email(user_id, email):
    return EmailChange(user_id=user_id, email=email, next=None).send()


@task()
def mail_updated_email(user_id):
    return EmailUpdated(user_id=user_id).send()


@task()
def mail_password_reset(user_id):
    return PasswordReset(user_id=user_id).send()
