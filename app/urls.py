from django.urls import path

from app.views import (
    home,
    stop_thread,
    start_thread,
    configure_antonia,
    create_card,
    delete_card,
    CardList,
    sign_out,
    sign_in,

)

app_name = "app"

urlpatterns = [
    path("", view=home, name="home"),
    path("app/signout", view=sign_out, name="sign_out"),
    path("app/signin", view=sign_in, name="sign_in"),

    path("app/thread/stop", view=stop_thread, name="stop_thread"),
    path("app/thread/start", view=start_thread, name="start_thread"),
    path("configure", view=configure_antonia, name="configure"),

    path("create-card/", view=create_card, name="create-card"),
    path("cards/", view=CardList.as_view(), name="card-list"),
    path("delete-card/<int:pk>", view=delete_card, name="delete-card"),
]