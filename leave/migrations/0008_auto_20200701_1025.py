# Generated by Django 3.0.7 on 2020-07-01 10:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leave', '0007_auto_20200630_2318'),
    ]

    operations = [
        migrations.RenameField(
            model_name='employeeinstance',
            old_name='leave_resaon',
            new_name='leave_reason',
        ),
    ]
