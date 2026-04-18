from django.db import models
from accounts.models import User

class Notification(models.Model):
    TYPE_CHOICES = [
        ('message', 'New Message'),
        ('booking', 'Booking Update'),
        ('approval', 'Account Approval'),
        ('review', 'New Review'),
        ('general', 'General'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notif_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='general')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.content[:50]}"
