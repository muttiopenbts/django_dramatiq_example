# Generated by Django 3.1.5 on 2021-01-31 22:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0020_remove_rpc_timestamp'),
    ]

    operations = [
        migrations.AddField(
            model_name='rpc',
            name='timestamp',
            field=models.DateTimeField(default='2020-01-01 00:00:00.000000UTC'),
        ),
    ]
