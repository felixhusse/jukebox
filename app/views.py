from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
import pprint
import spotipy
import threading
from spotipy.oauth2 import SpotifyOAuth
from .models import Configuration
from .forms import ConfigurationForm
from .services import SpotifyConnection, RFIDCardReader
from .threads import RFIDReaderThread

scope = "user-read-playback-state,user-modify-playback-state"
spotify_connection = SpotifyConnection(scope=scope)

def home(request):
    if not spotify_connection.is_configured:
        messages.add_message(request, messages.WARNING, "Please configure system!")
        return render(
            request,
            "pages/home.html",
            {}
        )

    cache_handler = spotipy.cache_handler.DjangoSessionCacheHandler(request=request)
    spotify_connection.set_cache_handler(cache_handler=cache_handler)

    if request.GET.get('code'):
        spotify_connection.get_auth_manager().get_access_token(request.GET.get('code'))
        return redirect("app:home")

    if not spotify_connection.get_auth_manager().validate_token(cache_handler.get_cached_token()):
        auth_url = spotify_connection.get_auth_manager().get_authorize_url()
        return render(
            request,
            "pages/home.html",
            {"auth_url": auth_url}, )

    spotify = spotipy.Spotify(auth_manager=spotify_connection.get_auth_manager())
    devices = spotify.devices()
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(devices)
    return render(
        request,
        "pages/home.html",
        {"data": devices},)


def play_song(request):
    spotify = spotipy.Spotify(auth_manager=spotify_connection.get_auth_manager())
    if request.GET.get('speaker'):
        spotify.start_playback(uris=['spotify:track:6jk4wqqbpSJu6Thlsa3GLo'], device_id=request.GET.get('speaker'))
    else:
        spotify.start_playback(uris=['spotify:track:6jk4wqqbpSJu6Thlsa3GLo'])
    messages.add_message(request, messages.SUCCESS, "Song started")
    return JsonResponse({"result": "Done", "messages": prepare_messages(request)})


def stop_song(request):
    spotify = spotipy.Spotify(auth_manager=spotify_connection.get_auth_manager())

    spotify.pause_playback()
    messages.add_message(request, messages.SUCCESS, "Song paused")
    return JsonResponse({"result": "Done", "messages": prepare_messages(request)})

def train_card(request):
    try:
        rfid_reader = RFIDCardReader()
        if request.GET.get('spotify_uid'):
            spotify_uid = request.GET.get('spotify_uid')
            rfid_reader.train_card(spotify_uid=spotify_uid)
            messages.add_message(request, messages.SUCCESS, "Card succesfully trained")
    except NameError:
        messages.add_message(request, messages.ERROR, "Named exception")
    return JsonResponse({"result": "Done", "messages": prepare_messages(request)})

def stop_thread(request):
    threads = threading.enumerate()
    for thread in threads:
        if thread.name == "RFID_Thread":
            thread.event.set()
            messages.add_message(request, messages.SUCCESS, "Thread stopped")

    return JsonResponse({"result": "Done", "messages": prepare_messages(request)})

def start_thread(request):
    threads = threading.enumerate()
    for thread in threads:
        if thread.name == "RFID_Thread":
            messages.add_message(request, messages.SUCCESS, "Thread already running")
            return JsonResponse({"result": "Done", "messages": prepare_messages(request)})

    event = threading.Event()
    thread = RFIDReaderThread(event)
    thread.start()
    messages.add_message(request, messages.SUCCESS, "Thread started")
    return JsonResponse({"result": "Done", "messages": prepare_messages(request)})



def configure_antonia(request):
    if Configuration.objects.all().count() == 0:
        form = ConfigurationForm(request.POST or None)

        if request.method == "POST":
            if form.is_valid():
                form.save()
                return redirect('home')
        context = {
            "form": form
        }
        return render(request, 'pages/configuration.html', context)
    else:
        data = Configuration.objects.first()
        form = ConfigurationForm(instance=data)

        if request.method == "POST":
            form = ConfigurationForm(request.POST, instance=data)
            if form.is_valid():
                form.save()
                return redirect ('home')
        context = {
            "form": form
        }
        return render(request, 'pages/configuration.html', context)




def prepare_messages(request):
    django_messages = []
    for message in messages.get_messages(request):
        django_messages.append(
            {
                "level": message.level,
                "message": message.message,
                "extra_tags": message.tags,
            }
        )
    return django_messages
