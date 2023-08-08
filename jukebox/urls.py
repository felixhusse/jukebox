"""
URL configuration for jukebox project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import logging
import threading
from app.threads import RFIDReaderThread
from app.services import PushButtonService
from django.contrib import admin
from django.urls import path, include
import sys


urlpatterns = [
    path("", include("app.urls", namespace="app")),
    path('admin/', admin.site.urls),
]
if not sys.argv[0].endswith('manage.py'):
    try:
        logger = logging.getLogger(__name__)
        logger.info("Fire up RFID Reader Thread")
        event = threading.Event()
        thread = RFIDReaderThread(event)
        thread.start()
        pushbutton_service = PushButtonService()
        logger.warning("ThreadDetails: {} ({}) {}".format(thread.name, thread.ident, thread.daemon))
    except Exception as e:
        logging.exception("Startup Thread Exception")
