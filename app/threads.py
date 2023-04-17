from threading import Thread, Event
import time
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
        from app.models import Configuration
        from app.services import RFIDCardReader
        print('RFIDReaderThread running')
        reader = SimpleMFRC522()
        configuration = Configuration.objects.first()
        if configuration:
            print("Configuration found")
            while not self.event.is_set():
                id, text = reader.read_no_block()
                print("ID: %s\nText: %s" % (id, text))
                time.sleep(0.5)

        print("Finished")
