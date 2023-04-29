from django.apps import AppConfig
import os
import logging
import threading
try:
    import RPi.GPIO as GPIO
except ImportError:
    from .mockups import GPIO

class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'
    logger = logging.getLogger(__name__)

    def ready(self):
        if os.environ.get('RUN_MAIN'):
            self.logger.info("Fire up RFID Reader Thread")
            from app.threads import RFIDReaderThread
            event = threading.Event()
            thread = RFIDReaderThread(event)
            thread.start()
            self.logger.warning("ThreadDetails: {} ({}) {}".format(thread.name, thread.ident, thread.daemon))





