from django.apps import AppConfig
from threading import Thread


class RFIDReaderThread(Thread):

    def run(self):
        print('RFIDReaderThread running')



class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        from app.models import Configuration
        RFIDReaderThread().start()