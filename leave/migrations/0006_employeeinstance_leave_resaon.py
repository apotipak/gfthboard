# Generated by Django 3.0.7 on 2020-06-30 23:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leave', '0005_auto_20200621_2242'),
    ]

    operations = [
        migrations.AddField(
            model_name='employeeinstance',
            name='leave_resaon',
            field=models.TextField(blank=True, null=True),
        ),
    ]