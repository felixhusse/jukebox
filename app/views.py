from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic.list import ListView
import pprint
import spotipy
import threading
from spotipy.oauth2 import SpotifyOAuth
from .models import Configuration, MusicCard
from .forms import ConfigurationForm
from .services import SpotifyConnection, RFIDCardReader, SpotifyPlayer, AntoniaService
from .threads import RFIDReaderThread



def home(request):
    scope = "user-read-playback-state,user-modify-playback-state"
    spotify_connection = SpotifyConnection(scope=scope)

    if not spotify_connection.is_configured:
        messages.add_message(request, messages.WARNING, "Please configure system!")
        return render(
            request,
            "pages/home.html",
            {}
        )

    if request.GET.get('code'):
        spotify_connection.get_auth_manager().get_access_token(request.GET.get('code'))
        return redirect("app:home")

    if not spotify_connection.get_auth_manager().validate_token(spotify_connection.get_auth_manager().get_cached_token()):
        auth_url = spotify_connection.get_auth_manager().get_authorize_url()
        return render(
            request,
            "pages/home.html",
            {"auth_url": auth_url}, )

    spotify = spotipy.Spotify(auth_manager=spotify_connection.get_auth_manager())
    devices = spotify.devices()
    return render(
        request,
        "pages/home.html",
        {"data": devices},)


def play_song(request):
    scope = "user-read-playback-state,user-modify-playback-state"
    spotify_connection = SpotifyConnection(scope=scope)
    spotify = spotipy.Spotify(auth_manager=spotify_connection.get_auth_manager())

    urn = 'spotify:album:1cOFQWQW6BHrLbSiuQfsdO'
    album = spotify.album(urn)
    tracks = []
    for track in album['tracks']['items']:
        tracks.append(track['uri'])

    if request.GET.get('speaker'):
        spotify.start_playback(uris=tracks, device_id=request.GET.get('speaker'))
    else:
        spotify.start_playback(uris=['spotify:track:70JdQ8artpCN4NBn7Wt1Uw'])
    messages.add_message(request, messages.SUCCESS, "Song started")
    return JsonResponse({"result": "Done", "messages": prepare_messages(request)})


def stop_song(request):
    scope = "user-read-playback-state,user-modify-playback-state"
    spotify_connection = SpotifyConnection(scope=scope)
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
                messages.add_message(request, messages.SUCCESS, "config saved")
                return redirect('app:configure')
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
                messages.add_message(request, messages.SUCCESS, "config saved")
                return redirect('app:configure')
        context = {
            "form": form
        }
        return render(request, 'pages/configuration.html', context)


def create_card(request):
    spotify_uid = request.POST.get('spotify_uid')
    spotify_type = request.POST.get('spotify_type')
    music_type = MusicCard.Type(spotify_type)
    rfid_reader = RFIDCardReader()
    card_uid = rfid_reader.read_uid()
    scope = "user-read-playback-state,user-modify-playback-state"
    spotify_details = SpotifyPlayer(spotiy_connection=SpotifyConnection(scope=scope)).load_detail(
        spotify_uid=spotify_uid, card_type=music_type)
    AntoniaService.train_card(card_uid=card_uid, spotify_uid=spotify_uid, spotify_type=music_type,
                              spotify_details=spotify_details)
    messages.add_message(request, messages.SUCCESS, "Card succesfully trained")
    cards = MusicCard.objects.all()
    return render(request, 'pages/card-list.html', {"cards": cards})

def delete_card(request, pk):
    # remove the contact from list.
    card_id = MusicCard.objects.get(id=pk)
    card_id.delete()
    cards = MusicCard.objects.all()
    return render(request, 'pages/card-list.html', {'cards': cards})

class CardList(ListView):
    template_name = "pages/card.html"
    model = MusicCard
    context_object_name = 'cards'





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
