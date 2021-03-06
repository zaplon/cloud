# Generated by Django 2.1.7 on 2019-08-25 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medicine', '0013_auto_20190720_2356'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='prescription',
            options={'ordering': ('-date',)},
        ),
        migrations.AddField(
            model_name='medicinetoprescription',
            name='amount',
            field=models.CharField(default='', max_length=128),
        ),
        migrations.AlterField(
            model_name='medicinetoprescription',
            name='dosage',
            field=models.CharField(default='', max_length=128),
        ),
    ]
