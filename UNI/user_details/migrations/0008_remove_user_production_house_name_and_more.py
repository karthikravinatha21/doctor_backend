# Generated by Django 5.2 on 2025-05-22 18:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('production_house', '0004_delete_productionhouseownership'),
        ('user_details', '0007_user_full_name_user_production_house_name_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='production_house_name',
        ),
        migrations.AddField(
            model_name='user',
            name='production_house',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_production_house', to='production_house.productionhouse'),
        ),
    ]
