import pprint

from django import forms
from .models import Configuration, MusicCard
from .services import SpotifyConnection, SpotifyPlayer


def retrieve_devices():
    scope = "user-read-playback-state,user-modify-playback-state"
    spotify_connection = SpotifyConnection(scope=scope)

    if not spotify_connection.is_configured:
        return [("default", "default")]

    spotify_player = SpotifyPlayer(spotiy_connection=spotify_connection)
    devices = spotify_player.find_devices()["devices"]
    device_list = []
    for device in devices:
        device_list.append((device["id"], device["name"]))

    return device_list


class CardForm(forms.ModelForm):
    spotify_uid = forms.CharField(widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Spotify UID"
    }))

    spotify_music_type = forms.ChoiceField(choices=MusicCard.Type, widget=forms.Select(attrs={
        "class": "form-control",
        "placeholder": "Music Type"
    }))

    class Meta:
        fields = ["spotify_uid", "spotify_music_type"]
        model = MusicCard


class ConfigurationForm(forms.ModelForm):

    spotify_client_id = forms.CharField(widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "client id"
    }))
    spotify_client_secret = forms.CharField(widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "client secret"
    }))

    spotify_callback_url = forms.CharField(widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "callback url"
    }))

    class Meta:
        model = Configuration
        fields = [
            'spotify_client_id', 'spotify_client_secret', 'spotify_callback_url','spotify_speaker_id','reader_type', 'jukebox_spotify_type', 'jukebox_volume'
        ]
