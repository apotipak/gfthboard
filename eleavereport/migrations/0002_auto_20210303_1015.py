# Generated by Django 3.0.7 on 2021-03-03 10:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('eleavereport', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='eleavereports',
            options={'permissions': (('can_view_m1_report', 'Can view M1 report'),)},
        ),
    ]
