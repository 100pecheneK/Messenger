from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User
import json


def log_in(request):
    return render(request, 'Chat/log_in.html', {})


@login_required
def chat_choice(request):
    if request.user.is_superuser:
        users = User.objects.exclude(is_superuser=True)
    else:
        users = User.objects.filter(username=request.user)

    context = {
        'users': users,
    }
    return render(request, 'Chat/chat_choice.html', context)


@login_required
def chat_for_all(request):
    context = {
        'superuser_check': request.user.is_superuser,
    }
    return render(request, 'Chat/chat_for_all.html', context)


@login_required
def room(request, room_name):
    try:
        user = User.objects.get(username=room_name)
        url_user = user.username
    except User.DoesNotExist:
        return False
    context = {
        'room_name_json': mark_safe(json.dumps(url_user)),
        'current_user': mark_safe(json.dumps(request.user.username)),
        'username': mark_safe(json.dumps(url_user)),
    }

    return render(request, 'Chat/room.html', context)
