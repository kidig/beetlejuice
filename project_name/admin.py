from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe

from .models import User

admin.site.unregister(Group)


class AvatarMixin:
    @staticmethod
    def avatar_image(obj):
        avatar = obj.avatar
        if not avatar:
            return ''

        html = '<span style="display: inline-block; width: 40px; height: 40px; background: url({});' \
               ' background-size: cover" />'.format(obj.avatar['x80'])
        return mark_safe(html)

    @staticmethod
    def avatar(obj):
        return UserAdmin.avatar_image(obj)

    @staticmethod
    def avatar_full(obj):
        avatar = obj.avatar
        if not avatar:
            return ''

        html = '<span style="display: inline-block; width: 300px; height: 300px; background: url({});' \
               ' background-size: cover" />'.format(obj.avatar['x300'])
        return mark_safe(html)


@admin.register(User)
class UserAdmin(BaseUserAdmin, AvatarMixin):
    list_display = (
        'id', 'avatar', 'first_name', 'last_name', 'email', 'email_confirmed', 'is_active', 'is_staff',
    )
    list_filter = ('is_active', 'is_staff', 'date_joined',)
    search_fields = ('email', 'first_name', 'last_name',)
    readonly_fields = (
        'id', 'last_login', 'date_joined', 'avatar_image', 'avatar_full',
    )
    ordering = ('-date_joined',)
    fieldsets = (
        (None, {'fields': ('email', 'email_confirmed', 'password')}),
        ('Personal info', {'fields': ('avatar_full', 'first_name', 'last_name',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
