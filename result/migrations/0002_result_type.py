# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-05-29 09:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('result', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='type',
            field=models.CharField(choices=[('IMAGE', 'Zdj\u0119cie'), ('DOCUMENT', 'Dokument'), ('VIDEO', 'Film')], default='DOCUMENT', max_length=20),
        ),
    ]
