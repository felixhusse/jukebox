from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
import pprint
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from .models import Configuration
from .forms import ConfigurationForm




def home(request):

    if (Configuration.objects.all().count()==0):
        messages.add_message(request, messages.WARNING, "Please configure system!")
        return render(
            request,
            "pages/home.html",
            {}
        )

    configuration = Configuration.objects.first()
    scope = "user-read-playback-state,user-modify-playback-state"
    cache_handler = spotipy.cache_handler.DjangoSessionCacheHandler(request=request)
    auth_manager = SpotifyOAuth(scope=scope,
                                client_id=configuration.spotify_client_id,
                                client_secret=configuration.spotify_client_secret,
                                redirect_uri=configuration.spotify_callback_url,
                                cache_handler=cache_handler,
                                show_dialog=True)

    if request.GET.get('code'):
        auth_manager.get_access_token(request.GET.get('code'))
        return redirect("app:home")

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        auth_url = auth_manager.get_authorize_url()
        return render(
            request,
            "pages/home.html",
            {"auth_url": auth_url}, )

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    devices = spotify.devices()
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(devices)
    return render(
        request,
        "pages/home.html",
        {"data": devices},)


def play_song(request):

    scope = "user-read-playback-state,user-modify-playback-state"
    configuration = Configuration.objects.first()
    cache_handler = spotipy.cache_handler.DjangoSessionCacheHandler(request=request)
    auth_manager = SpotifyOAuth(scope=scope,
                                client_id=configuration.spotify_client_id,
                                client_secret=configuration.spotify_client_secret,
                                redirect_uri=configuration.spotify_callback_url,
                                cache_handler=cache_handler,
                                show_dialog=True)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    if request.GET.get('speaker'):
        spotify.start_playback(uris=['spotify:track:6jk4wqqbpSJu6Thlsa3GLo'], device_id=request.GET.get('speaker'))
    else:
        spotify.start_playback(uris=['spotify:track:6jk4wqqbpSJu6Thlsa3GLo'])
    messages.add_message(request, messages.SUCCESS, "Song started")
    return JsonResponse({"result": "Done", "messages": prepare_messages(request)})


def stop_song(request):
    configuration = Configuration.objects.first()
    scope = "user-read-playback-state,user-modify-playback-state"
    cache_handler = spotipy.cache_handler.DjangoSessionCacheHandler(request=request)
    auth_manager = SpotifyOAuth(scope=scope,
                                client_id=configuration.spotify_client_id,
                                client_secret=configuration.spotify_client_secret,
                                redirect_uri=configuration.spotify_callback_url,
                                cache_handler=cache_handler,
                                show_dialog=True)
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    spotify.pause_playback()
    messages.add_message(request, messages.SUCCESS, "Song paused")
    return JsonResponse({"result": "Done", "messages": prepare_messages(request)})


def create(request):
    form = ConfigurationForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect ('home')
    context = {
        "form": form
    }
    return render(request, 'pages/configuration.html', context)


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
            "form":form
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
