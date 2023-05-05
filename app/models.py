from django.db import models

# Create your models here.


class Configuration(models.Model):
    spotify_client_id = models.CharField(max_length=100)
    spotify_client_secret = models.CharField(max_length=100)
    spotify_callback_url = models.CharField(max_length=100)
    spotify_speaker_id = models.CharField(max_length=100, default="")

class MusicCard(models.Model):
    MUSIC_TYPE = [
        ("al", "Album"),
        ("tr", "Track"),
        ("pl", "Playlist"),
    ]
    spotify_uid = models.CharField(max_length=200)
    card_uid = models.CharField(max_length=200)
    music_type = models.CharField(max_length=2, choices=MUSIC_TYPE, default="tr")

