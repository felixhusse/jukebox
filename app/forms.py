import pprint

from django import forms
from .models import Configuration
from .services import SpotifyConnection, SpotifyPlayer
def retrieve_devices():
    scope = "user-read-playback-state,user-modify-playback-state"
    spotify_player = SpotifyPlayer(spotiy_connection=SpotifyConnection(scope=scope))
    devices = spotify_player.find_devices()["devices"]
    device_list = []
    for device in devices:
        device_list.append((device["id"], device["name"]))

    return device_list

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

    spotify_speaker_id = forms.ChoiceField(choices=retrieve_devices, widget=forms.Select(attrs={
        "class": "form-control",
        "placeholder": "speaker id"
    }))

    class Meta:
        model = Configuration
        fields = [
            'spotify_client_id', 'spotify_client_secret', 'spotify_callback_url','spotify_speaker_id',
        ]
