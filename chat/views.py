from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Conversation, Message
from partners.models import Partner
from notifications.models import Notification

@login_required
def conversation_list(request):
    user = request.user
    if hasattr(user, 'partner'):
        conversations = Conversation.objects.filter(partner=user.partner).order_by('-created_at')
    else:
        conversations = Conversation.objects.filter(user=user).order_by('-created_at')
    return render(request, 'chat/list.html', {'conversations': conversations})

@login_required
def conversation_detail(request, pk):
    conversation = get_object_or_404(Conversation, pk=pk)
    user = request.user
    if conversation.user != user and conversation.partner.user != user:
        messages.error(request, 'Access denied.')
        return redirect('chat:list')
    msgs = conversation.messages.order_by('created_at')
    return render(request, 'chat/detail.html', {'conversation': conversation, 'messages': msgs})

@login_required
def start_conversation(request, partner_id):
    partner = get_object_or_404(Partner, pk=partner_id, is_approved=True)
    user = request.user
    if hasattr(user, 'partner'):
        messages.error(request, 'Partners cannot initiate chats with other partners.')
        return redirect('partners:list')
    conversation, created = Conversation.objects.get_or_create(user=user, partner=partner)
    if created:
        Notification.objects.create(
            user=partner.user,
            notif_type='message',
            content=f'{user.username} started a conversation with you.'
        )
    return redirect('chat:detail', pk=conversation.pk)
