# Generated by Django 3.0.12 on 2021-05-06 09:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0008_auto_20210501_1906'),
    ]

    operations = [
        migrations.AddField(
            model_name='outlookemailactiveuserlist',
            name='is_licensed',
            field=models.BooleanField(default=False),
        ),
    ]
