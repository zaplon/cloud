# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2018-06-02 23:30
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0029_note_private'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='specialization',
            options={'verbose_name': 'Specjalizacja', 'verbose_name_plural': 'Specjalizacje'},
        ),
    ]
