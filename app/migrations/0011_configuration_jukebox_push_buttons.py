# Generated by Django 4.2 on 2023-05-17 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_remove_musiccard_music_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuration',
            name='jukebox_push_buttons',
            field=models.JSONField(default={'backward': 12, 'forward': 10}),
        ),
    ]