# Generated by Django 2.1.7 on 2019-12-04 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0049_remove_nfzsettings_id_pracownika_oid_ext'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='birth_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]