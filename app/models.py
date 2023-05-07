from enum import Enum

from django.db import models


# Create your models here.

class CardChoices(Enum):
    AL = "Album"
    PL = "Playlist"
    TR = "Track"


class Configuration(models.Model):
    spotify_client_id = models.CharField(max_length=100)
    spotify_client_secret = models.CharField(max_length=100)
    spotify_callback_url = models.CharField(max_length=100)
    spotify_speaker_id = models.CharField(max_length=100, default="")


class MusicCard(models.Model):
    spotify_uid = models.CharField(max_length=200)
    card_uid = models.CharField(max_length=200)
    music_type = models.CharField(max_length=2, choices=[(tag, tag.value) for tag in CardChoices], default=CardChoices.TR.name)
    spotify_name = models.CharField(max_length=200, default="")
    spotify_track_num = models.IntegerField(default=0)
    spotify_cover_url = models.CharField(max_length=200, blank=True, default="")
    last_played = models.DateTimeField(blank=True, null=True)
