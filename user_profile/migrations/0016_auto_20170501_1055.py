# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-05-01 10:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0015_auto_20170501_1051'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctor',
            name='working_hours',
            field=models.CharField(blank=True, max_length=800, null=True),
        ),
    ]
