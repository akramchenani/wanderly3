from django.db import models
from accounts.models import User
from partners.models import Partner
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'partner')

    def __str__(self):
        return f"{self.user.username} ↔ {self.partner.user.username}"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"

    def is_expired(self):
        expiry = self.created_at + timedelta(days=settings.CHAT_MESSAGE_EXPIRY_DAYS)
        return timezone.now() > expiry
