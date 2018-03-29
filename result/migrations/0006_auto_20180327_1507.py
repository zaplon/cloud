# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2018-03-27 15:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('result', '0005_auto_20170611_2132'),
    ]

    operations = [
        migrations.AlterField(
            model_name='result',
            name='type',
            field=models.CharField(choices=[('IMAGE', 'Zdjęcie'), ('DOCUMENT', 'Dokument'), ('VIDEO', 'Film'), ('ENDOSCOPE_VIDEO', 'Film'), ('ENDOSCOPE_IMAGE', 'Zdjęcie')], default='DOCUMENT', max_length=20),
        ),
    ]