# prod.py
# Production settings for myapp
from . import *  # Import base settings from settings/__init__.py
from . import env

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {"level": env('LOG_LEVEL'), "handlers": ["file"]},
    "handlers": {
        "file": {
            "level": env('LOG_LEVEL'),
            "class": "logging.FileHandler",
            "filename": "/var/log/jukebox.log",
            "formatter": "app",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": env('LOG_LEVEL'),
            "propagate": True
        },
    },
    "formatters": {
        "app": {
            "format": (
                u"%(asctime)s [%(levelname)-8s] "
                "(%(module)s.%(funcName)s) %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
}