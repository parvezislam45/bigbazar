from django.urls import path
from .views import chat_view, conversation_list, start_conversation

urlpatterns = [
    path('chat/<int:conversation_id>/', chat_view, name='chat'),
    path('conversations/', conversation_list, name='conversation_list'),
    path('chat/start/<int:user_id>/', start_conversation, name='start_conversation'),
]
