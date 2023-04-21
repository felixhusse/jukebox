from threading import Thread, Event
import time
import spotipy
try:
    import RPi.GPIO as GPIO
    from mfrc522 import SimpleMFRC522
except ImportError:
    import app.fake_gpio as GPIO
    from .mockups import SimpleMFRC522


class RFIDReaderThread(Thread):
    reader = None
    def __init__(self, event):
        super(RFIDReaderThread, self).__init__(name="RFID_Thread", daemon=True)
        self.reader = SimpleMFRC522()
        # store the event
        self.event = event

    def run(self):
        from app.models import Configuration, MusicCard
        from app.services import SpotifyConnection
        print('RFIDReaderThread running')
        configuration = Configuration.objects.first()
        try:
            if configuration:
                print("Configuration found")
                while not self.event.is_set():
                    uid = self.reader.read_id_no_block()
                    if uid:
                        musiccard = MusicCard.objects.filter(card_uid=uid)
                        if musiccard:
                            scope = "user-read-playback-state,user-modify-playback-state"
                            spotify_connection = SpotifyConnection(scope=scope)
                            spotify = spotipy.Spotify(auth_manager=spotify_connection.get_auth_manager())
                            spotify.start_playback(uris=['spotify:{}'.format(musiccard.first().spotify_uid)])
                            print("Song started")
                    time.sleep(0.5)
        finally:
            self.reader.READER.Close_MFRC522()
        print("Finished")
