# Generated by Django 3.0.12 on 2021-04-29 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0006_outlookemailactiveuserlist'),
    ]

    operations = [
        migrations.AddField(
            model_name='outlookemailactiveuserlist',
            name='emp_id',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=7, null=True),
        ),
    ]