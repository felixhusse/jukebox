# Generated by Django 4.2 on 2023-05-05 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_musiccard_music_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuration',
            name='spotify_speaker_id',
            field=models.CharField(default='', max_length=100),
        ),
    ]
