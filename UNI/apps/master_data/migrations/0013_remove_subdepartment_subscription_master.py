# Generated by Django 5.2 on 2025-06-27 11:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('master_data', '0012_subdepartment_subscription_master'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subdepartment',
            name='subscription_master',
        ),
    ]
