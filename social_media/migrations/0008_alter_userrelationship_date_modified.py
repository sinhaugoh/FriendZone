# Generated by Django 4.0.2 on 2022-02-20 04:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social_media', '0007_alter_userrelationship_date_modified'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userrelationship',
            name='date_modified',
            field=models.DateTimeField(auto_now=True),
        ),
    ]