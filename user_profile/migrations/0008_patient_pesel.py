# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-09 13:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0007_auto_20170109_1315'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='pesel',
            field=models.CharField(blank=True, max_length=11, null=True),
        ),
    ]
