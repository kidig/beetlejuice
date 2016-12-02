# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-02 17:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import easy_thumbnails.fields
import project_name.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('new_email', models.EmailField(blank=True, db_index=True, max_length=254, null=True)),
                ('email_confirm_code', models.TextField(blank=True, null=True)),
                ('new_email_confirm_code', models.TextField(blank=True, null=True)),
                ('email_confirmed', models.BooleanField(default=False)),
                ('password_reset_code', models.TextField(blank=True, null=True)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('avatar_url', models.TextField(blank=True, null=True)),
                ('avatar_image', easy_thumbnails.fields.ThumbnailerImageField(blank=True, null=True, upload_to=project_name.models.User.avatar_image_path)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
