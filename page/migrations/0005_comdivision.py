# Generated by Django 3.0.7 on 2020-07-07 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('page', '0004_userprofile_username'),
    ]

    operations = [
        migrations.CreateModel(
            name='ComDivision',
            fields=[
                ('div_id', models.DecimalField(decimal_places=0, max_digits=3, primary_key=True, serialize=False)),
                ('com_id', models.DecimalField(blank=True, decimal_places=0, max_digits=2, null=True)),
                ('div_th', models.CharField(blank=True, max_length=50, null=True)),
                ('div_en', models.CharField(blank=True, max_length=50, null=True)),
                ('upd_date', models.DateTimeField(blank=True, null=True)),
                ('upd_by', models.CharField(blank=True, max_length=10, null=True)),
                ('upd_flag', models.CharField(blank=True, max_length=1, null=True)),
            ],
            options={
                'db_table': 'COM_DIVISION',
                'permissions': (('can_view_all_employees', 'Can view all employees'),),
                'managed': False,
            },
        ),
    ]