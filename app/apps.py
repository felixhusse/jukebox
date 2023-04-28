from django.apps import AppConfig
import threading
import logging
try:
    import RPi.GPIO as GPIO
except ImportError:
    from .mockups import GPIO

class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'
    logger = logging.getLogger(__name__)

    def ready(self):
        GPIO.cleanup()
        threads = threading.enumerate()
        thread_running = False
        for thread in threads:
            if thread.name == "RFID_Thread":
                thread_running = True
                break
        #if not thread_running:
            #from app.threads import RFIDReaderThread
            #event = threading.Event()
            #thread = RFIDReaderThread(event)
            #thread.start()
            #self.logger.warning("ThreadDetails: {} ({}) {}".format(thread.name, thread.ident, thread.daemon))




