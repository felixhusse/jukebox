import logging
import sys
import spotipy.cache_handler
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException
try:
    import RPi.GPIO as GPIO
    from app.rfcreader import HigherGainSimpleMFRC522 as SimpleMFRC522
except ImportError:
    from app.mockups import SimpleMFRC522, GPIO

from .models import Configuration, MusicCard, CardChoices

class SpotifyConnection:
    logger = logging.getLogger(__name__)
    def __init__(self, scope="user-read-playback-state,user-modify-playback-state"):
        if Configuration.objects.all().count() == 1:
            configuration = Configuration.objects.first()
            self.cache_handler = spotipy.cache_handler.CacheFileHandler()
            self.auth_manager = SpotifyOAuth(scope=scope,
                                            client_id=configuration.spotify_client_id,
                                            client_secret=configuration.spotify_client_secret,
                                            redirect_uri=configuration.spotify_callback_url,
                                            show_dialog=True,
                                            cache_handler=self.cache_handler)
            self.is_configured = True
        else:
            self.is_configured = False

    def get_auth_manager(self):
        return self.auth_manager


class SpotifyPlayer:
    logger = logging.getLogger(__name__)
    spotipy_spotify = None

    def __init__(self, spotiy_connection):
        self.spotify_connection = spotiy_connection
        self.spotipy_spotify = spotipy.Spotify(auth_manager=self.spotify_connection.get_auth_manager())

    def load_detail(self, spotify_uid, card_type):
        result = {}
        spotify_result = None

        if CardChoices.TR == card_type:
            spotify_track = self.spotipy_spotify.track(spotify_uid)
            result['name'] = spotify_track['name']
            result['num_of_tracks'] = 1
            for image in spotify_track['album']['images']:
                if image["height"] == 300:
                    result['image_url'] = image['url']
                    break
            return result
        elif CardChoices.AL == card_type:
            spotify_result = self.spotipy_spotify.album(spotify_uid)
            result['num_of_tracks'] = spotify_result['total_tracks']
        elif CardChoices.PL == card_type:
            spotify_result = self.spotipy_spotify.playlist(spotify_uid)
            result['num_of_tracks'] = spotify_result['tracks']['total']

        result['name'] = spotify_result['name']
        for image in spotify_result['images']:
            if image["height"] == 300:
                result['image_url'] = image['url']
                break
        return result

    def find_devices(self):
        return self.spotipy_spotify.devices()

    def play_song(self, spotify_uid):
        track_uris = []
        if "album" in spotify_uid:
            album = self.spotipy_spotify.album('spotify:{}'.format(spotify_uid))
            for track in album['tracks']['items']:
                track_uris.append(track['uri'])
        else:
            track_uris.append('spotify:{}'.format(spotify_uid))
        self.spotipy_spotify.start_playback(uris=track_uris)

    def stop_song(self):
        self.spotipy_spotify.pause_playback()


class RFIDCardReader:
    def __init__(self):
        self.reader = SimpleMFRC522()

    def train_card(self, spotify_uid):
        try:
            id, text = self.reader.read()
            print("Card read")
            cards = MusicCard.objects.filter(card_uid=id)
            if cards:
                card = cards.first()
                card.spotify_uid = spotify_uid
                card.save()
            else:
                card = MusicCard(
                    card_uid=id,
                    spotify_uid=spotify_uid
                )
                card.save()
        finally:
            self.reader.READER.Close_MFRC522()
            GPIO.cleanup()

