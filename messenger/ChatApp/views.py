from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User
import json
from .models import Room, Message
from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect


# Изменения:убрал ненужные вьюхи

@login_required
def chat_choice(request):
    # if request.user.is_superuser:
    #     users = User.objects.exclude(is_superuser=True)
    # else:
    #     users = User.objects.filter(username=request.user)

    # Тут поиск
    search_query = request.GET.get('search', '')

    if request.user.is_superuser:
        rooms = Room.objects.all()
        is_admin = True
        if search_query:
            rooms = Room.objects.filter(name__icontains=search_query)
    else:
        rooms = Room.objects.filter(name=request.user)

    context = {
        'page': 2,
        'users': rooms,
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
