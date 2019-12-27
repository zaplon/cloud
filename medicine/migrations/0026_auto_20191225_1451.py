# Generated by Django 2.1.7 on 2019-12-25 13:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('visit', '0017_icd10_visits'),
        ('medicine', '0025_prescription_deleted'),
    ]

    operations = [
        migrations.AddField(
            model_name='prescription',
            name='tmp',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='prescription',
            name='visit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='prescriptions', to='visit.Visit'),
        ),
    ]