# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-04-26 18:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0011_note'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='misal_id',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='patient',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='Email'),
        ),
        migrations.AlterField(
            model_name='patient',
            name='first_name',
            field=models.CharField(default='', max_length=100, verbose_name='Imi\u0119'),
        ),
        migrations.AlterField(
            model_name='patient',
            name='last_name',
            field=models.CharField(default='', max_length=100, verbose_name='Nazwisko'),
        ),
        migrations.AlterField(
            model_name='patient',
            name='mobile',
            field=models.IntegerField(blank=True, null=True, verbose_name='Telefon'),
        ),
        migrations.AlterField(
            model_name='patient',
            name='pesel',
            field=models.CharField(blank=True, max_length=11, null=True, verbose_name='Pesel'),
        ),
    ]
