# Generated by Django 3.0.7 on 2020-06-21 22:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leave', '0004_auto_20200616_0923'),
    ]

    operations = [
        migrations.AddField(
            model_name='employeeinstance',
            name='document',
            field=models.FileField(null=True, upload_to='documents/'),
        ),
        migrations.AddField(
            model_name='employeeinstance',
            name='uploaded_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
