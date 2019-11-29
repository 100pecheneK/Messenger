from django.urls import path

from . import views


app_name = 'Chat'
urlpatterns = [
    path('', views.log_in, name='index'),
    path('all/', views.chat_for_all, name='chat_for_all'),
    path('chat_choice/', views.chat_choice, name='chat_choice'),
    path('<str:room_name>/', views.room, name='room'),
]