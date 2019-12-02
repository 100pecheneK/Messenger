from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User
import json
from .models import Room
from django.core import serializers
from django.http import HttpResponse


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
    # Get user and user_admin
    try:
        user = User.objects.get(username=room_name)
        user_admin = User.objects.get(is_superuser=True)
    except User.DoesNotExist:
        return False
    # Get current_room or create
    try:
        current_room = Room.objects.get(name=room_name)
    except Room.DoesNotExist:
        Room.objects.create(name=room_name, user_simple=user,
                            user_admin=user_admin)
        current_room = Room.objects.get(name=room_name)
    
    try:
        messages = current_room.message_set.all()
        # messages = serializers.serialize('json', messages)
        # return HttpResponse(messages, content_type='application/json')
    except:
        print('Error str 51 in views.py')

    context = {
        'messages': messages,
        'current_room_name': mark_safe(json.dumps(current_room.name)),
        'room_name_json': mark_safe(json.dumps(user.username)),
        'current_user': mark_safe(json.dumps(request.user.username)),
        'username': mark_safe(json.dumps(user.username)),
    }

    return render(request, 'Chat/room.html', context)
