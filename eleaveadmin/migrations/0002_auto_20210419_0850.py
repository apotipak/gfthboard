# Generated by Django 3.0.12 on 2021-04-19 08:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('eleaveadmin', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='eleaveadmin',
            options={'permissions': (('is_eleave_admin', 'This is an eleave administrator'), ('can_create_m1_leave_request', 'Can create M1 leave request'), ('can_create_m5_leave_request', 'Can create M5 leave request'))},
        ),
    ]
