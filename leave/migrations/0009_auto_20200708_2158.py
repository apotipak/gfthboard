# Generated by Django 3.0.7 on 2020-07-08 21:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leave', '0008_auto_20200701_1025'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='leaveemployee',
            options={'managed': False, 'ordering': ['emp_id'], 'permissions': (('approve_leaveplan', 'Can approve leave employee'),)},
        ),
    ]
