# Generated by Django 3.0.12 on 2021-05-10 08:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ITcontract', '0022_itcontractemailalert'),
    ]

    operations = [
        migrations.AddField(
            model_name='itcontractdb',
            name='turn_off_notification',
            field=models.BooleanField(default=False),
        ),
    ]