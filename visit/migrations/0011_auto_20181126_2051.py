# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2018-11-26 20:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visit', '0010_auto_20181125_2103'),
    ]

    operations = [
        migrations.AlterField(
            model_name='visittab',
            name='type',
            field=models.CharField(max_length=32),
        ),
    ]
