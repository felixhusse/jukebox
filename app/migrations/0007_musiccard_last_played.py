# Generated by Django 4.2 on 2023-05-07 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_musiccard_spotify_cover_musiccard_spotify_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='musiccard',
            name='last_played',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
