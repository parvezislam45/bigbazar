from django.shortcuts import render, get_object_or_404, redirect
from .models import Conversation, Message
from accounts.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q

@login_required
def conversation_list(request):
    conversations = Conversation.objects.filter(participants=request.user).order_by('-updated')
    return render(request, 'chat.html', {
        'conversations': conversations
    })

@login_required
def chat_view(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)

    if request.user not in conversation.participants.all():
        return redirect('conversation_list')

    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            Message.objects.create(conversation=conversation, sender=request.user, message=message)

    messages = conversation.messages.all()

    # Determine the other participant
    other = conversation.participants.exclude(id=request.user.id).first()

    return render(request, 'chat_box.html', {
        'messages': messages,
        'conversation': conversation,
        'receiver': other,
        'user': request.user,
    })

@login_required
def start_conversation(request, user_id):
    other_user = get_object_or_404(User, id=user_id)

    # Check if conversation exists
    conversation = Conversation.objects.filter(participants=request.user).filter(participants=other_user).first()

    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, other_user)

    return redirect('chat', conversation_id=conversation.id)
