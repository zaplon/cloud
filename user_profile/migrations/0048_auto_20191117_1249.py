# Generated by Django 2.1.7 on 2019-11-17 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0047_auto_20191112_1047'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='gender',
            field=models.CharField(choices=[('M', 'Mężczyzna'), ('F', 'Kobieta')], default='', max_length=1, verbose_name='Płeć'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='systemsettings',
            name='postal_code',
            field=models.CharField(blank=True, max_length=6, verbose_name='Kod pocztowy'),
        ),
    ]
