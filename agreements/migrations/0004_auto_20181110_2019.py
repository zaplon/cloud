# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2018-11-10 20:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agreements', '0003_auto_20180327_1507'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agreement',
            name='title',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='Title'),
        ),
    ]