from django.db.models import Q
from .models import ChatThread

def get_or_create_thread(user1, user2):
    thread = ChatThread.objects.filter(
        Q(user1=user1, user2=user2) | Q(user1=user2, user2=user1)
    ).first()
    if not thread:
        thread = ChatThread.objects.create(user1=user1, user2=user2)
    return thread
