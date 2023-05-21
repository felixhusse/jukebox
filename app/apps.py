from django.apps import AppConfig
import os
import sys
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
        if not sys.argv[0].endswith('manage.py'):
            if os.environ.get('DEV') and os.environ.get('RUN_MAIN'):
                self.logger.info("Fire up RFID Reader Thread for DEV Env")
                from app.threads import RFIDReaderThread
                from app.services import PushButtonService
                event = threading.Event()
                thread = RFIDReaderThread(event)
                thread.start()
                pushbutton_service = PushButtonService()
                self.logger.warning("ThreadDetails: {} ({}) {}".format(thread.name, thread.ident, thread.daemon))
            elif os.environ.get('RUN_MAIN'):
                self.logger.info("Fire up RFID Reader Thread for Prod Env")
                from app.threads import RFIDReaderThread
                from app.services import PushButtonService
                event = threading.Event()
                thread = RFIDReaderThread(event)
                thread.start()
                pushbutton_service = PushButtonService()
                self.logger.warning("ThreadDetails: {} ({}) {}".format(thread.name, thread.ident, thread.daemon))






