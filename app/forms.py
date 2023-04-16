from django import forms
from .models import Configuration

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
            'spotify_client_id', 'spotify_client_secret', 'spotify_callback_url'
        ]
