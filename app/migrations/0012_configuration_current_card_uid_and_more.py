# Generated by Django 4.2 on 2023-08-07 13:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_configuration_jukebox_push_buttons'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuration',
            name='current_card_uid',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AlterField(
            model_name='musiccard',
            name='spotify_music_type',
            field=models.CharField(choices=[('AL', 'album'), ('PL', 'playlist'), ('TR', 'track')], default='TR', max_length=2),
        ),
    ]
