# Generated by Django 2.1.7 on 2019-11-23 10:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medicine', '0020_auto_20191115_1836'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicinetoprescription',
            name='number',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]