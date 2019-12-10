from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User
import json
from .models import Room, Message
from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect
from dataclasses import dataclass
from django.db.models.query import QuerySet


@dataclass
class RoomNameAndUser:
    room_name: str
    user: QuerySet


@login_required
def chat_choice(request):
    room_name_and_user = list()
    if request.user.is_superuser:
        try:
            rooms_qs = Room.objects.exclude(name=request.user.username)
            for room in rooms_qs:
                room_name_and_user.append(
                    RoomNameAndUser(
                        room_name=room.name,
                        user=room.user_simple
                    )
                )
        except Room.DoesNotExist:
            pass
    else:
        try:
            room = Room.objects.get(name=request.user.username)
            room_name_and_user.append(
                RoomNameAndUser(
                    room_name=room.name,
                    user=room.user_admin
                )
            )
        except Room.DoesNotExist:
            pass
    context = {
        'page': 2,
        'room_name_and_user': room_name_and_user,
        'page_title': 'Диалоги',
    }
    return render(request, 'Chat/chat_choice.html', context)


@permission_required('polls.can_vote')
def distribution(request):
    if request.user.is_superuser:
        users = User.objects.exclude(is_superuser=True)
    else:
        users = User.objects.filter(username=request.user)

    context = {
        'page': 2,
        'page_title': 'Групповая рассылка',
        'users': users,
    }
    return render(request, 'Chat/distribution.html', context)


@permission_required('polls.can_vote')
def save_distribution(request):
    try:
        content = request.POST['content']
    except:
        content = ''
    users = request.POST.getlist('search')
    for user in users:
        author = User.objects.get(username=request.user)
        current_room = Room.objects.get(name=user)
        Message.objects.create(content=content, author=author, room=current_room)
    return HttpResponseRedirect(reverse('Chat:chat_choice'))


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
        messages = current_room.message.all()
    except:
        messages = None

    if request.user == user_admin:
        if user.first_name != '' and user.last_name != '':
            page_title = f'{user.first_name} {user.last_name}'
        else:
            page_title = user.username
    elif request.user == user:
        if user_admin.first_name != '' and user_admin.last_name != '':
            page_title = f'{user_admin.first_name} {user_admin.last_name}'
        else:
            page_title = user_admin.username
    context = {
        'page_title': page_title,
        'messages': messages,
        'current_room_name': mark_safe(json.dumps(current_room.name)),
        'room_name_json': mark_safe(json.dumps(user.username)),
        'current_user': mark_safe(json.dumps(request.user.username)),
        'username': mark_safe(json.dumps(user.username)),
    }

    return render(request, 'Chat/room.html', context)
