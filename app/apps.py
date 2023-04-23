from django.apps import AppConfig
import threading

class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        threads = threading.enumerate()
        thread_running = False
        for thread in threads:
            if thread.name == "RFID_Thread":
                thread_running = True
                break
        if not thread_running:
            from app.threads import RFIDReaderThread
            event = threading.Event()
            thread = RFIDReaderThread(event)
            thread.start()
            print("ThreadDetails: {} ({}) {}".format(thread.name, thread.ident, thread.daemon))




