# Generated by Django 3.0.12 on 2021-04-21 01:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ITcontract', '0007_delete_itcontractalert'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScheduleAlertSetting',
            fields=[
                ('alert_id', models.AutoField(primary_key=True, serialize=False)),
                ('alert_name', models.CharField(blank=True, max_length=100, null=True)),
                ('alert_description', models.CharField(blank=True, max_length=100, null=True)),
                ('alert_email', models.CharField(blank=True, max_length=100, null=True)),
                ('active', models.CharField(blank=True, max_length=1, null=True)),
                ('minimum_day', models.SmallIntegerField(blank=True, null=True)),
                ('created_date', models.DateTimeField(null=True)),
                ('created_by', models.CharField(blank=True, max_length=50, null=True)),
                ('modified_date', models.DateTimeField(null=True)),
                ('modified_by', models.CharField(blank=True, max_length=50, null=True)),
                ('modified_flag', models.CharField(blank=True, max_length=1, null=True)),
            ],
            options={
                'db_table': 'it_contract_alert',
                'ordering': ('alert_id',),
                'managed': True,
            },
        ),
    ]
