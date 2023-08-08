import sys
from threading import Thread, Event
import time
import logging
from app.rfid import reader
from spotipy import SpotifyException


class RFIDReaderThread(Thread):
    logger = logging.getLogger(__name__)
    reader = None
    def __init__(self, event):
        super(RFIDReaderThread, self).__init__(name="RFID_Thread", daemon=True)
        self.reader = reader.Reader(0xffff, 0x0035, 84, 16, should_reset=True, debug=True)
        self.reader.initialize()
        # store the event
        self.event = event

    def stop_reader(self):
        self.reader.disconnect()

    def run(self):
        from app.models import Configuration, MusicCard
        from app.services import SpotifyConnection, SpotifyPlayer
        self.logger.info('RFIDReaderThread running')
        configuration = Configuration.objects.first()
        scope = "user-read-playback-state,user-modify-playback-state"
        spotify_player = SpotifyPlayer(spotiy_connection=SpotifyConnection(scope=scope))

        none_count = 0
        try:
            if configuration:
                configuration.current_card_uid = ""
                configuration.save()

                while not self.event.is_set():
                    try:
                        card_uid = self.reader.read()
                        current_card = MusicCard.objects.filter(card_uid=card_uid).first()
                        self.logger.debug("Card is read: {0}".format(card_uid))
                        if current_card:
                            self.logger.debug("Track linked {0}".format(current_card.spotify_name))
                            configuration = Configuration.objects.first()
                            if configuration.current_card_uid == card_uid:
                                spotify_player.stop_song()
                                configuration = Configuration.objects.first()
                                configuration.current_card_uid = ""
                                configuration.save()
                            else:
                                spotify_type = current_card.get_spotify_music_type_display().lower()
                                spotify_uid = current_card.spotify_uid
                                spotify_player.play_song(spotify_uid, spotify_type)
                                configuration.current_card_uid = card_uid
                                configuration.save()
                    except SpotifyException as e:
                        self.logger.error("Spotify Exception: " + str(e))
                    time.sleep(0.1)
        except Exception as e:
            logging.exception("RFID Reader Thread Exception")
        finally:
            self.reader.disconnect()
        print("Reader closed")
