# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-04-29 20:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0012_auto_20170426_1838'),
    ]

    operations = [
        migrations.CreateModel(
            name='Code',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.IntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
