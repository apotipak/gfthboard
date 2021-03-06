# Generated by Django 3.0.12 on 2021-06-17 00:13

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('page', '0021_auto_20210616_1716'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserLoginLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('emp_id', models.DecimalField(blank=True, decimal_places=0, max_digits=7, null=True)),
                ('login_date', models.DateTimeField(blank=True, default=datetime.date.today, null=True)),
                ('ip_address', models.CharField(blank=True, max_length=20, null=True)),
                ('device', models.CharField(blank=True, max_length=100, null=True)),
                ('created_by', models.CharField(blank=True, default='system', max_length=10, null=True)),
                ('upd_by', models.CharField(blank=True, max_length=10, null=True)),
                ('upd_flag', models.CharField(blank=True, default='A', max_length=1, null=True)),
            ],
            options={
                'db_table': 'auth_user_login_log',
                'managed': True,
            },
        ),
    ]
