# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-28 13:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0003_doctor_working_hours'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='visit_duration',
            field=models.IntegerField(default=15),
        ),
    ]
