from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def notification_list(request):
    notifs = Notification.objects.filter(user=request.user).order_by('-created_at')
    notifs.filter(is_read=False).update(is_read=True)
    return render(request, 'notifications/list.html', {'notifications': notifs})

@login_required
def mark_read(request, pk):
    notif = Notification.objects.filter(pk=pk, user=request.user).first()
    if notif:
        notif.is_read = True
        notif.save()
    return redirect('notifications:list')
