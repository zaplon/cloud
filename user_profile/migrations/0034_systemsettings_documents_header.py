# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2018-11-24 17:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0033_auto_20181110_2019'),
    ]

    operations = [
        migrations.AddField(
            model_name='systemsettings',
            name='documents_header',
            field=models.TextField(blank=True, verbose_name='Nagłówek dokumentów'),
        ),
    ]
