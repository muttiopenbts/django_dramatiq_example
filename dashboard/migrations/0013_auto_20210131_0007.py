# Generated by Django 3.1.5 on 2021-01-31 08:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0012_rpc_output'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rpc',
            name='params',
            field=models.IntegerField(default='', help_text='Parameters to RPC'),
        ),
    ]
