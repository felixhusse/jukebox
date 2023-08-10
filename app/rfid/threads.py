import sys
from threading import Thread, Event
import time
import logging
from app.rfid import neuftechreader
from spotipy import SpotifyException

import RPi.GPIO as GPIO
from app.rfid.rfcreader import HigherGainSimpleMFRC522 as SimpleMFRC522


from app.services import SpotifyConnection, SpotifyPlayer
from app.models import Configuration, MusicCard

class RFIDReaderThread(Thread):
    logger = logging.getLogger(__name__)
    reader = None

    def __init__(self, event, reader_type):
        super(RFIDReaderThread, self).__init__(name="RFID_Thread", daemon=True)
        if reader_type == Configuration.ReaderType.NEUFTECH:
            self.reader = neuftechreader.NeuftechReader(0xffff, 0x0035, 84, 16, should_reset=False)
            self.reader.initialize()
        elif reader_type == Configuration.ReaderType.MFRC522:
            self.reader = SimpleMFRC522()
        self.event = event

    def stop_playback(self):
        scope = "user-read-playback-state,user-modify-playback-state"
        spotify_player = SpotifyPlayer(spotiy_connection=SpotifyConnection(scope=scope))
        spotify_player.stop_song()
        configuration = Configuration.objects.first()
        configuration.current_card_uid = ""
        configuration.save()

    def start_playback(self, current_card):
        scope = "user-read-playback-state,user-modify-playback-state"
        spotify_player = SpotifyPlayer(spotiy_connection=SpotifyConnection(scope=scope))
        spotify_player.play_song(current_card.spotify_uid, current_card.get_spotify_music_type_display().lower())
        configuration = Configuration.objects.first()
        configuration.current_card_uid = current_card.card_uid
        configuration.save()

    def run_mfrc522(self):
        playing_song = False
        none_count = 0
        while not self.event.is_set():
            card_uid = self.reader.read_id_no_block()
            try:
                if card_uid and not playing_song:
                    self.logger.debug("Card read: {0}".format(card_uid))
                    current_card = MusicCard.objects.filter(card_uid=card_uid).first()
                    if current_card:
                        self.logger.debug("+-> Track linked: {0}".format(current_card.spotify_name))
                        self.start_playback(current_card=current_card)
                        playing_song = True
                elif card_uid and playing_song:
                    none_count = 0
                elif not card_uid and playing_song:
                    none_count = none_count + 1
                    if none_count > 1:
                        self.stop_playback()
                        playing_song = False
                        none_count = 0
                        self.logger.info("Song stopped")
            except SpotifyException as e:
                self.logger.error("Spotify Exception: " + str(e))
            time.sleep(0.5)

    def run_neuftech(self):
        try:
            while not self.event.is_set():
                try:
                    card_uid = self.reader.read()
                    current_card = MusicCard.objects.filter(card_uid=card_uid).first()
                    self.logger.debug("Card read: {0}".format(card_uid))
                    if current_card:
                        self.logger.debug("+-> Track linked: {0}".format(current_card.spotify_name))
                        configuration = Configuration.objects.first()
                        if configuration.current_card_uid == card_uid:
                            self.stop_playback()
                        else:
                            self.logger.debug("+-> Track linked: {0}".format(current_card.spotify_name))
                            self.start_playback(current_card=current_card)
                except SpotifyException as e:
                    self.logger.error("Spotify Exception: " + str(e))
                time.sleep(0.1)
        except Exception as e:
            logging.exception("RFID Reader Thread Exception")
        finally:
            self.reader.disconnect()
        print("Reader closed")

    def run(self):
        configuration = Configuration.objects.first()
        if Configuration.ReaderType.NEUFTECH == configuration.reader_type:
            self.logger.info('Neuftech Reader running')
            self.run_neuftech()
        elif Configuration.ReaderType.MFRC522 == configuration.reader_type:
            self.logger.info('MFRC522 Reader running')
            self.run_mfrc522()
