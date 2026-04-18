from django.db import models
from accounts.models import User
from partners.models import Partner

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name='ratings')
    stars = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'partner')

    def __str__(self):
        return f"{self.user.username} rated {self.partner} - {self.stars}★"
