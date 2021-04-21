# Generated by Django 3.0.12 on 2021-04-21 07:31

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ITcontract', '0021_delete_schedulealertsetting'),
    ]

    operations = [
        migrations.CreateModel(
            name='ITContractEmailAlert',
            fields=[
                ('alert_id', models.AutoField(primary_key=True, serialize=False)),
                ('app_name', models.CharField(blank=True, max_length=100, null=True)),
                ('description', models.CharField(blank=True, max_length=100, null=True)),
                ('send_to_email', models.CharField(blank=True, max_length=100, null=True)),
                ('send_to_group_email', models.CharField(blank=True, max_length=100, null=True)),
                ('alert_active', models.CharField(blank=True, max_length=1, null=True)),
                ('reach_minimum_day', models.SmallIntegerField(blank=True, null=True)),
                ('created_date', models.DateTimeField(default=datetime.date.today, null=True)),
                ('created_by', models.CharField(blank=True, default='System', max_length=50, null=True)),
                ('modified_date', models.DateTimeField(null=True)),
                ('modified_by', models.CharField(blank=True, max_length=50, null=True)),
                ('modified_flag', models.CharField(blank=True, max_length=1, null=True)),
            ],
            options={
                'db_table': 'itcontract_email_alert',
                'ordering': ('alert_id',),
                'managed': True,
            },
        ),
    ]
