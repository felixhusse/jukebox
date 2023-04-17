from django.apps import AppConfig
import threading
from .threads import RFIDReaderThread

class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        event = threading.Event()
        from app.models import Configuration
        thread = RFIDReaderThread(event)
        thread.start()
        print("ThreadDetails: {} ({}) {}".format(thread.name, thread.ident, thread.daemon))



