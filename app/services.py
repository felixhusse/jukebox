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

from .models import Configuration, MusicCard

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

    spotipy_spotify = None

    def __init__(self, spotiy_connection):
        self.spotify_connection = spotiy_connection
        self.spotipy_spotify = spotipy.Spotify(auth_manager=self.spotify_connection.get_auth_manager())

    def play_song(self, spotify_uid):
        track_uris = []
        if "album" in spotify_uid:
            album = self.spotipy_spotify.album('spotify:{}'.format(spotify_uid))
            for track in album['tracks']['items']:
                track_uris.append(track['uri'])
        else:
            track_uris.append('spotify:{}'.format(spotify_uid))
        try:
            self.spotipy_spotify.start_playback(uris=track_uris)
        except SpotifyException as e:
            self.logger.error("Failed to play song: " + str(e))
        except Exception as e:
            ex_type, ex_value, ex_traceback = sys.exc_info()
            self.logger.error("%s : %s".format(ex_type, ex_value))

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

