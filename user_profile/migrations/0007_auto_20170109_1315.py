# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-09 13:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0006_auto_20170102_1112'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='first_name',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='patient',
            name='last_name',
            field=models.CharField(default='', max_length=100),
        ),
    ]
