# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2019-03-09 16:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medicine', '0010_auto_20181125_2103'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicineparent',
            name='user_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
