# Generated by Django 3.1.5 on 2021-01-31 22:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0017_auto_20210131_1432'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rpc',
            name='timestamp',
            field=models.DateTimeField(default='2020-01-01 00:00:00'),
        ),
    ]
