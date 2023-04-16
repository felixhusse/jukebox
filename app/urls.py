from django.urls import path

from app.views import (
    home,
    play_song,
    stop_song,
    configure_antonia,
)

app_name = "app"

urlpatterns = [
    path("", view=home, name="home"),
    path("app/play", view=play_song, name="play_song"),
    path("app/stop", view=stop_song, name="stop_song"),
    path("configure", view=configure_antonia, name="configure"),
]