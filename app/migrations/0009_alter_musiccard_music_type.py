# Generated by Django 4.2 on 2023-05-08 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_remove_musiccard_spotify_cover_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='musiccard',
            name='music_type',
            field=models.CharField(choices=[('AL', 'Album'), ('PL', 'Playlist'), ('TR', 'Track')], default='TR', max_length=2),
        ),
    ]