# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-05-19 11:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0020_doctor_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='specializations',
            field=models.ManyToManyField(related_name='doctors', to='user_profile.Specialization'),
        ),
    ]
