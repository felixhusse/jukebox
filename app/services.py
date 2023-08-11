import logging
import os
import spotipy.cache_handler
from spotipy.oauth2 import SpotifyOAuth


from .rfid import neuftechreader

try:
    import RPi.GPIO as GPIO
except ImportError:
    from Mock import GPIO

from .models import Configuration, MusicCard


class AntoniaService:
    @staticmethod
    def train_card(card_uid, spotify_uid, spotify_type, spotify_details):
        logger = logging.getLogger(__name__)
        cards = MusicCard.objects.filter(card_uid=card_uid)
        if cards:
            card = cards.first()
            card.spotify_uid = spotify_uid
            card.spotify_music_type = spotify_type
            card.spotify_cover_url = spotify_details["image_url"],
            card.spotify_track_num = spotify_details["num_of_tracks"],
            card.spotify_name = spotify_details['name'],
            card.save()
        else:
            logger.debug("Creating new Card")
            logger.debug(spotify_type)
            card = MusicCard(
                card_uid=card_uid,
                spotify_uid=spotify_uid,
                spotify_music_type=spotify_type,
                spotify_cover_url=spotify_details["image_url"],
                spotify_track_num=spotify_details["num_of_tracks"],
                spotify_name=spotify_details['name'],
            )
            card.save()
    @staticmethod
    def delete_card(card_uid):
        cards = MusicCard.objects.filter(card_uid=card_uid)
        if cards:
            card = cards.first()
            card.delete()

class SpotifyConnection:
    logger = logging.getLogger(__name__)
    logged_in = False

    def __init__(self, scope="user-read-playback-state,user-modify-playback-state"):
        self.scope = scope
        self.cache_handler = spotipy.cache_handler.CacheFileHandler()
        if Configuration.objects.all().count() == 1:
            configuration = Configuration.objects.first()
            self.is_configured = True
            self.auth_manager = SpotifyOAuth(scope=self.scope,
                                             client_id=configuration.spotify_client_id,
                                             client_secret=configuration.spotify_client_secret,
                                             redirect_uri=configuration.spotify_callback_url,
                                             show_dialog=True,
                                             cache_handler=self.cache_handler)
            if self.auth_manager.validate_token(self.cache_handler.get_cached_token()):
                self.logged_in = True
            else:
                self.logged_in = False

        else:
            self.is_configured = False

    def login(self):
        configuration = Configuration.objects.first()
        self.auth_manager = SpotifyOAuth(scope=self.scope,
                                         client_id=configuration.spotify_client_id,
                                         client_secret=configuration.spotify_client_secret,
                                         redirect_uri=configuration.spotify_callback_url,
                                         show_dialog=True,
                                         cache_handler=self.cache_handler)
        auth_url = self.auth_manager.get_authorize_url()
        self.logged_in = True
        return auth_url

    def set_auth_token(self, code):
        self.auth_manager.get_access_token(code)
        self.logged_in = True

    def clear_cache(self):
        cache_file = '.cache'
        os.remove(cache_file)


class SpotifyPlayer:
    logger = logging.getLogger(__name__)
    spotipy_spotify = None

    def __init__(self, spotiy_connection):
        self.spotify_connection = spotiy_connection
        self.spotipy_spotify = spotipy.Spotify(auth_manager=self.spotify_connection.auth_manager)

    def load_detail(self, spotify_uid, card_type):
        result = {}
        spotify_result = None

        if MusicCard.Type.TRACK == card_type:
            spotify_result = self.spotipy_spotify.track(spotify_uid)
            result['num_of_tracks'] = 1
            images = spotify_result['album']['images']
        elif MusicCard.Type.ALBUM == card_type:
            spotify_result = self.spotipy_spotify.album(spotify_uid)
            result['num_of_tracks'] = spotify_result['total_tracks']
            images = spotify_result['images']
        elif MusicCard.Type.PLAYLIST == card_type:
            spotify_result = self.spotipy_spotify.playlist(spotify_uid)
            result['num_of_tracks'] = spotify_result['tracks']['total']
            images = spotify_result['images']

        result['name'] = spotify_result['name']
        for image in images:
            result['image_url'] = image['url']
            if image["height"] == 300:
                result['image_url'] = image['url']
                break
        return result

    def find_devices(self):
        return self.spotipy_spotify.devices()

    def play_song(self, spotify_uid, spotify_type):
        track_uris = []
        configuration = Configuration.objects.first()
        if "album" == spotify_type:
            album = self.spotipy_spotify.album(album_id=spotify_uid)
            for track in album['tracks']['items']:
                track_uris.append(track['uri'])
        elif "playlist" == spotify_type:
            track_uris = []
            playlist = self.spotipy_spotify.playlist_items(playlist_id=spotify_uid)
            for track in playlist['items']:
                track_uris.append(track['track']['uri'])
        else:
            track_uris.append('spotify:{0}:{1}'.format(spotify_type,spotify_uid))
        self.spotipy_spotify.start_playback(device_id=configuration.spotify_speaker_id,uris=track_uris)

    def __get_current_volume(self):
        spotify_result = self.spotipy_spotify.current_playback()

        return spotify_result["device"]["volume_percent"]

    def volume_up(self):
        current_volume = self.__get_current_volume()

        if current_volume < 100:
            volume = current_volume+10
            if volume > 100:
                self.spotipy_spotify.volume(volume_percent=100)
            else:
                self.spotipy_spotify.volume(volume_percent=volume)

    def volume_down(self):
        current_volume = self.__get_current_volume()
        if current_volume > 0:
            volume = current_volume-10
            if volume < 0:
                self.spotipy_spotify.volume(volume_percent=0)
            else:
                self.spotipy_spotify.volume(volume_percent=volume)

    def next_song(self):
        self.spotipy_spotify.next_track()

    def previous_song(self):
        self.spotipy_spotify.previous_track()

    def stop_song(self):
        self.spotipy_spotify.pause_playback()


class PushButtonService:
    logger = logging.getLogger(__name__)
    forward_counter = 0
    backward_counter = 0
    spotify_player = None

    def button_volup(self, channel):
        self.spotify_player.volume_up()
        self.forward_counter += 1
        self.logger.debug("{}# Volume UP Button was pushed!".format(self.forward_counter))

    def button_voldown(self, channel):
        self.spotify_player.volume_down()
        self.backward_counter += 1
        self.logger.debug("{}# Volume Down Button was pushed!".format(self.backward_counter))

    def __init__(self):
        scope = "user-read-playback-state,user-modify-playback-state"
        self.spotify_player = SpotifyPlayer(spotiy_connection=SpotifyConnection(scope=scope))
        GPIO.setwarnings(True)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(8, GPIO.RISING, callback=self.button_volup, bouncetime=500)
        GPIO.add_event_detect(10, GPIO.RISING, callback=self.button_voldown, bouncetime=500)
