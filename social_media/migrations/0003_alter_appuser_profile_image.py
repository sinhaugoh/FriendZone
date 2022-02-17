# Generated by Django 4.0.2 on 2022-02-17 09:14

from django.db import migrations, models
import social_media.models
import social_media.storage


class Migration(migrations.Migration):

    dependencies = [
        ('social_media', '0002_alter_appuser_profile_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appuser',
            name='profile_image',
            field=models.ImageField(blank=True, default='images/default_images/default_profile.png', max_length=256, null=True, storage=social_media.storage.OverwriteFileStorage(), upload_to=social_media.models.get_profile_image_path),
        ),
    ]