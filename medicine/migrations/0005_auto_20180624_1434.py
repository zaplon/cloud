# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2018-06-24 14:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medicine', '0004_auto_20180605_0955'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='medicinetoprescription',
            name='dose',
        ),
        migrations.AddField(
            model_name='prescription',
            name='nfz',
            field=models.CharField(default='', max_length=16),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='prescription',
            name='permissions',
            field=models.CharField(default='', max_length=16),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='medicinetoprescription',
            name='notes',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
