from django.urls import path

from app.views import (
    home,
    play_song,
    stop_song,
    train_card,
    stop_thread,
    start_thread,
    configure_antonia,
    cards,

)

app_name = "app"

urlpatterns = [
    path("", view=home, name="home"),
    path("app/play", view=play_song, name="play_song"),
    path("app/stop", view=stop_song, name="stop_song"),
    path("app/train", view=train_card, name="train_card"),
    path("app/thread/stop", view=stop_thread, name="stop_thread"),
    path("app/thread/start", view=start_thread, name="start_thread"),
    path("configure", view=configure_antonia, name="configure"),
    path("cards", view=cards, name="cards"),
]