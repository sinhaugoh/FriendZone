from django.urls import path
from .views import chat_room

urlpatterns = [
    path('<int:chat_target_id>/', chat_room, name='chat_room'),
]
