# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-05-24 13:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0021_doctor_specializations'),
    ]

    operations = [
        migrations.CreateModel(
            name='SystemSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('logo', models.ImageField(upload_to=b'', verbose_name='Logo')),
            ],
            options={
                'permissions': (('view_system_settings', 'Mo\u017ce edytowa\u0107 ustawienia systemu'),),
            },
        ),
    ]
