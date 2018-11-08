# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2018-06-05 09:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('medicine', '0003_prescription'),
    ]

    operations = [
        migrations.CreateModel(
            name='MedicineToPrescription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dosage', models.CharField(max_length=128)),
                ('dose', models.CharField(max_length=128)),
                ('notes', models.CharField(max_length=128)),
                ('medicine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='medicine.Medicine')),
            ],
        ),
        migrations.RemoveField(
            model_name='prescription',
            name='body',
        ),
        migrations.AddField(
            model_name='prescription',
            name='number',
            field=models.CharField(default='123', max_length=16),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='medicinetoprescription',
            name='prescription',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='medicine.Prescription'),
        ),
        migrations.AddField(
            model_name='medicinetoprescription',
            name='refundation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='medicine.Refundation'),
        ),
        migrations.AddField(
            model_name='prescription',
            name='medicines',
            field=models.ManyToManyField(related_name='prescriptions', through='medicine.MedicineToPrescription', to='medicine.Medicine'),
        ),
    ]