# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-06-06 18:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0027_auto_20170530_2228'),
        ('result', '0002_result_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='doctor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='results', to='user_profile.Doctor'),
        ),
    ]
