from django.apps import AppConfig
import sys, logging, threading


try:
    import RPi.GPIO as GPIO
except ImportError:
    from .mockups import GPIO

class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'
    logger = logging.getLogger(__name__)

    def ready(self):
        from app.models import Configuration
        from rfid.threads import RFIDReaderThread
        from services import PushButtonService, PsstPlayer

        if not sys.argv[0].endswith('manage.py'):
            try:
                logger = logging.getLogger(__name__)
                logger.info("Fire up RFID Reader Thread")
                event = threading.Event()
                configuration = Configuration.objects.first()
                thread = RFIDReaderThread(event=event, reader_type=configuration.reader_type)
                thread.start()
                pushbutton_service = PushButtonService()
                logger.warning("ThreadDetails: {} ({}) {}".format(thread.name, thread.ident, thread.daemon))
                if configuration.jukebox_spotify_type == Configuration.SpotifyType.PSST:
                    PsstPlayer.set_volume(0.6)

            except Exception as e:
                logging.exception("Startup Thread Exception")







