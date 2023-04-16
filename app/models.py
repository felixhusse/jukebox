from django.db import models

# Create your models here.


class Configuration(models.Model):
    spotify_client_id = models.CharField(max_length=100)
    spotify_client_secret = models.CharField(max_length=100)
    spotify_callback_url = models.CharField(max_length=100)
    linux_mode = models.BooleanField(default=False)
    