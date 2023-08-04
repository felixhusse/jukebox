from enum import Enum

from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.
class Configuration(models.Model):
    push_button_default = {
        "forward": 10,
        "backward": 12,
    }

    spotify_client_id = models.CharField(max_length=100)
    spotify_client_secret = models.CharField(max_length=100)
    spotify_callback_url = models.CharField(max_length=100)
    spotify_speaker_id = models.CharField(max_length=100, default="")
    current_card_uid = models.CharField(max_length=200, default="")
    jukebox_push_buttons = models.JSONField(default=push_button_default)


class MusicCard(models.Model):
    class Type(models.TextChoices):
        ALBUM = 'AL', _('album')
        PLAYLIST = 'PL', _('playlist')
        TRACK = 'TR', _('track')

    spotify_uid = models.CharField(max_length=200)
    card_uid = models.CharField(max_length=200)
    spotify_name = models.CharField(max_length=200, default="")
    spotify_track_num = models.IntegerField(default=0)
    spotify_cover_url = models.CharField(max_length=200, blank=True, default="")
    last_played = models.DateTimeField(blank=True, null=True)
    spotify_music_type = models.CharField(max_length=2, choices=Type.choices, default=Type.TRACK)

