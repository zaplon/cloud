# Generated by Django 2.1.7 on 2019-11-09 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medicine', '0018_prescription_external_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicinetoprescription',
            name='external_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='medicine',
            name='external_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
