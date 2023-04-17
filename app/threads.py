from threading import Thread, Event
import time
import spotipy
try:
    import RPi.GPIO as GPIO
    from mfrc522 import SimpleMFRC522
except ImportError:
    import app.fake_gpio as GPIO
    from .fake_rfc import SimpleMFRC522

class RFIDReaderThread(Thread):
    def __init__(self, event):
        super(RFIDReaderThread, self).__init__(name="RFID_Thread", daemon=True)
        # store the event
        self.event = event

    def run(self):
        from app.models import Configuration, MusicCard
        from app.services import SpotifyConnection
        print('RFIDReaderThread running')
        reader = SimpleMFRC522()
        configuration = Configuration.objects.first()
        if configuration:
            print("Configuration found")
            while not self.event.is_set():
                id, text = reader.read_no_block()
                if id:
                    musiccard = MusicCard.objects.filter(card_uid=id)
                    if musiccard:
                        scope = "user-read-playback-state,user-modify-playback-state"
                        spotify_connection = SpotifyConnection(scope=scope)
                        spotify = spotipy.Spotify(auth_manager=spotify_connection.get_auth_manager())
                        spotify.start_playback(uris=['spotify:track:{}'.format(musiccard.first().spotify_uid)], device_id='1b7e55f7da9e053ea3754c7f32aebf2d88274e1a')
                        print("Song started");
                time.sleep(0.5)

        print("Finished")
