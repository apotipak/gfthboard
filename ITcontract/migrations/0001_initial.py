# Generated by Django 3.0.7 on 2021-04-15 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ITcontractDB',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('dept', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'db_table': 'ITcontractDB',
                'ordering': ('id',),
                'managed': True,
            },
        ),
    ]
