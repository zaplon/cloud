# Generated by Django 2.1.7 on 2019-12-29 22:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0051_auto_20191222_1659'),
    ]

    operations = [
        migrations.AddField(
            model_name='nfzsettings',
            name='typ_podmiotu',
            field=models.CharField(choices=[('PRAKTYKA_LEKARSKA', 'Praktyka lekarska'), ('PODMIOT_LECZNICZY', 'Podmiot leczniczy')], default='PRAKTYKA_LEKARSKA', max_length=32),
        ),
        migrations.AlterField(
            model_name='profile',
            name='role',
            field=models.CharField(choices=[('doctor', 'Lekarz'), ('admin', 'Administrator')], max_length=10),
        ),
    ]
