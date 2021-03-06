# Generated by Django 3.0.12 on 2021-06-11 18:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('page', '0016_delete_covidemployeevaccineupdate'),
    ]

    operations = [
        migrations.CreateModel(
            name='CovidEmployeeVaccineUpdate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('emp_id', models.DecimalField(blank=True, decimal_places=0, max_digits=7, null=True)),
                ('full_name', models.CharField(blank=True, max_length=200, null=True)),
                ('phone_number', models.TextField(blank=True, max_length=50, null=True)),
                ('get_vaccine_status', models.DecimalField(blank=True, decimal_places=0, max_digits=1, null=True)),
                ('get_vaccine_date', models.DateTimeField(blank=True, null=True)),
                ('get_vaccine_place', models.CharField(blank=True, max_length=100, null=True)),
                ('file_attch', models.FileField(null=True, upload_to='documents/covid/')),
                ('file_attach_data', models.BinaryField(null=True)),
                ('file_attach_type', models.CharField(blank=True, max_length=10, null=True)),
                ('upd_date', models.DateTimeField(blank=True, null=True)),
                ('upd_by', models.CharField(blank=True, max_length=10, null=True)),
                ('upd_flag', models.CharField(blank=True, max_length=1, null=True)),
                ('op1', models.TextField(blank=True, max_length=10, null=True)),
                ('op2', models.TextField(blank=True, max_length=10, null=True)),
                ('opn1', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('opn2', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('opd1', models.DateTimeField(blank=True, null=True)),
                ('opd2', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'covid_employee_vaccine_update',
                'managed': True,
            },
        ),
    ]
