from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic.list import ListView
import logging
import spotipy
import threading
import os
from .models import Configuration, MusicCard
from .forms import ConfigurationForm
from .services import SpotifyConnection, SpotifyPlayer, AntoniaService, PushButtonService
from app.rfid.threads import RFIDReaderThread
from app.rfid import neuftechreader

try:
    import RPi.GPIO as GPIO
    from app.rfid.rfcreader import HigherGainSimpleMFRC522 as SimpleMFRC522
except ImportError:
    from Mock import GPIO
    from app.mockups import SimpleMFRC522

logger = logging.getLogger(__name__)

def home(request):
    scope = "user-read-playback-state,user-modify-playback-state"
    spotify_connection = SpotifyConnection(scope=scope)

    if not spotify_connection.is_configured:
        messages.add_message(request, messages.WARNING, "Please configure system!")
        return redirect("app:configure")

    if request.GET.get('code'):
        logger.debug("Code: %s", request.GET.get('code'))
        spotify_connection.set_auth_token(request.GET.get('code'))
        return redirect("app:home")

    if not spotify_connection.logged_in:
        return redirect("app:configure")

    spotify = spotipy.Spotify(auth_manager=spotify_connection.auth_manager)
    devices = spotify.devices()
    return render(
        request,
        "pages/home.html",
        {"data": devices}, )


def sign_in(request):
    spotify_connection = SpotifyConnection()
    auth_url = spotify_connection.login()
    messages.add_message(request, messages.SUCCESS, "Logging in")
    return redirect(auth_url)


def sign_out(request):
    logger.debug("Sign out")
    cache_file = '.cache'
    os.remove(cache_file)
    messages.add_message(request, messages.SUCCESS, "Logged out")
    return redirect("app:configure")


def stop_thread(request):
    threads = threading.enumerate()
    for thread in threads:
        if thread.name == "RFID_Thread":
            thread.event.set()
            GPIO.cleanup()
            messages.add_message(request, messages.SUCCESS, "Thread stopped")

    return JsonResponse({"result": "Done", "messages": prepare_messages(request)})


def start_thread(request):
    threads = threading.enumerate()
    for thread in threads:
        if thread.name == "RFID_Thread":
            messages.add_message(request, messages.SUCCESS, "Thread already running")
            return JsonResponse({"result": "Done", "messages": prepare_messages(request)})

    event = threading.Event()
    configuration = Configuration.objects.first()
    thread = RFIDReaderThread(event=event, reader_type=configuration.reader_type)
    thread.start()
    GPIO.cleanup()
    pushbutton_service = PushButtonService()
    messages.add_message(request, messages.SUCCESS, "Thread started")
    return JsonResponse({"result": "Done", "messages": prepare_messages(request)})


def configure_antonia(request):
    spotify_connection = SpotifyConnection()

    if Configuration.objects.all().count() == 0:
        form = ConfigurationForm(request.POST or None)

        if request.method == "POST":
            if form.is_valid():
                form.save()
                messages.add_message(request, messages.SUCCESS, "config saved")
                return redirect('app:configure')
        context = {
            "form": form,
            "logged_in": spotify_connection.logged_in,
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
            "form": form,
            "logged_in": spotify_connection.logged_in,
        }
        return render(request, 'pages/configuration.html', context)


def create_card(request):
    spotify_uid = request.POST.get('spotify_uid')
    spotify_type = request.POST.get('spotify_type')
    music_type = MusicCard.Type(spotify_type)
    configuration = Configuration.objects.first()
    card_uid = None
    if configuration.reader_type == Configuration.ReaderType.NEUFTECH:
        rfid_reader = neuftechreader.NeuftechReader(0xffff, 0x0035, 84, 16, should_reset=False)
        rfid_reader.initialize()
        card_uid = rfid_reader.read()
    elif configuration.reader_type == Configuration.ReaderType.MFRC522:
        rfid_reader = SimpleMFRC522()
        card_uid, payload = rfid_reader.read()

    if card_uid:
        scope = "user-read-playback-state,user-modify-playback-state"
        spotify_details = SpotifyPlayer(spotiy_connection=SpotifyConnection(scope=scope)).load_detail(
            spotify_uid=spotify_uid, card_type=music_type)
        AntoniaService.train_card(card_uid=card_uid, spotify_uid=spotify_uid, spotify_type=music_type,
                                  spotify_details=spotify_details)
        messages.add_message(request, messages.SUCCESS, "Card succesfully trained")
    else:
        messages.add_message(request, messages.ERROR, "Couldn't read Card UID")

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
