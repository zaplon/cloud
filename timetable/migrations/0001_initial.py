# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-05-19 10:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user_profile', '0020_doctor_title'),
        ('visit', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Term',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(verbose_name='Data')),
                ('status', models.CharField(choices=[('CANCELLED', 'Anulowany'), ('PENDING', 'Oczekuj\u0105cy'), ('FREE', 'Wolny'), ('FINISHED', 'Zako\u0144czony')], default='PENDING', max_length=10)),
                ('duration', models.IntegerField(default=15, verbose_name='Czas trwania (min)')),
                ('code', models.CharField(blank=True, max_length=50, null=True)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='terms', to='user_profile.Doctor', verbose_name='Lekarz')),
                ('patient', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='patient', to='user_profile.Patient', verbose_name='Pacjent')),
                ('visit', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='term', to='visit.Visit')),
            ],
        ),
    ]
