from threading import Thread, Event
import time
import logging
try:
    import RPi.GPIO as GPIO
    from app.rfcreader import HigherGainSimpleMFRC522 as SimpleMFRC522
except ImportError:
    from .mockups import SimpleMFRC522, GPIO

class RFIDReaderThread(Thread):
    logger = logging.getLogger(__name__)
    reader = None
    def __init__(self, event):
        super(RFIDReaderThread, self).__init__(name="RFID_Thread", daemon=True)
        self.reader = SimpleMFRC522()
        # store the event
        self.event = event

    def run(self):
        from app.models import Configuration, MusicCard
        from app.services import SpotifyConnection, SpotifyPlayer
        self.logger.info('RFIDReaderThread running')
        configuration = Configuration.objects.first()
        scope = "user-read-playback-state,user-modify-playback-state"
        spotify_player = SpotifyPlayer(spotiy_connection=SpotifyConnection(scope=scope))
        playing_song = False
        none_count = 0
        try:
            if configuration:
                while not self.event.is_set():
                    uid = self.reader.read_id_no_block()
                    if uid and not playing_song:
                        self.logger.debug("Card is read")
                        musiccard = MusicCard.objects.filter(card_uid=uid)
                        if musiccard:
                            spotify_player.play_song(musiccard.first().spotify_uid)
                            playing_song = True
                            none_count = 0
                            self.logger.info("Song started")
                    elif uid and playing_song:
                        none_count = 0
                    elif not uid and playing_song:
                        none_count = none_count + 1
                        if none_count > 1:
                            spotify_player.stop_song()
                            playing_song = False
                            none_count = 0
                            self.logger.info("Song stopped")

                    time.sleep(1.0)
        finally:

            self.reader.READER.Close_MFRC522()
        print("Finished")
