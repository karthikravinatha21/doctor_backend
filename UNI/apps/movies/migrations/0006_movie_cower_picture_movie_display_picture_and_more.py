# Generated by Django 5.2 on 2025-05-30 03:39

import apps.movies.models
import django.core.validators
import utils.constants
import utils.custom_storages
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0005_alter_actorportfolio_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='cower_picture',
            field=models.ImageField(blank=True, null=True, storage=utils.custom_storages.MediaStorage(), upload_to=apps.movies.models.generate_movie_images_path, validators=[django.core.validators.FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp']), utils.constants.validate_file_size, utils.constants.validate_file_authenticity]),
        ),
        migrations.AddField(
            model_name='movie',
            name='display_picture',
            field=models.ImageField(default=None, storage=utils.custom_storages.MediaStorage(), upload_to=apps.movies.models.generate_movie_images_path, validators=[django.core.validators.FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp']), utils.constants.validate_file_size, utils.constants.validate_file_authenticity]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='movie',
            name='duration_minutes',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
