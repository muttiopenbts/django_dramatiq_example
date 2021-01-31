# Generated by Django 3.1.5 on 2021-01-31 06:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0010_rpc_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='rpc',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('done', 'Done')], default='pending', max_length=7),
        ),
    ]
