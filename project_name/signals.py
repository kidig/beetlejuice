from django.dispatch import Signal

user_logged_in = Signal(providing_args=['user'])

user_switched_mode = Signal(providing_args=['user'])

user_email_confirm = Signal(providing_args=['user', 'next'])

user_new_email_confirm = Signal(providing_args=['user'])

email_confirmed = Signal(providing_args=['user'])

password_reset = Signal(providing_args=['user'])

signup_completed = Signal(providing_args=['user'])

user_avatar_updated = Signal(providing_args=['user'])
