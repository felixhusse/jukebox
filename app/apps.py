from django.apps import AppConfig
import logging

try:
    import RPi.GPIO as GPIO
except ImportError:
    from .mockups import GPIO

class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'
    logger = logging.getLogger(__name__)








