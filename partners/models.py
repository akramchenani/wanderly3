from django.db import models
from accounts.models import User

class Partner(models.Model):
    TYPE_CHOICES = [
        ('hotel', 'Hotel'),
        ('restaurant', 'Restaurant'),
        ('coffee', 'Coffee'),
        ('agency', 'Agency'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='partner')
    partner_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    description = models.TextField()
    profile_photo = models.ImageField(upload_to='partners/', blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    verification_document = models.FileField(upload_to='verifications/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.partner_type}"

class Hotel(models.Model):
    partner = models.OneToOneField(Partner, on_delete=models.CASCADE, related_name='hotel')
    city = models.ForeignKey('locations.City', on_delete=models.SET_NULL, null=True, blank=True)
    rating_avg = models.FloatField(default=0.0)

    def __str__(self):
        return f"Hotel: {self.partner.user.username}"

class Restaurant(models.Model):
    partner = models.OneToOneField(Partner, on_delete=models.CASCADE, related_name='restaurant')
    city = models.ForeignKey('locations.City', on_delete=models.SET_NULL, null=True, blank=True)
    rating_avg = models.FloatField(default=0.0)

    def __str__(self):
        return f"Restaurant: {self.partner.user.username}"

class Coffee(models.Model):
    partner = models.OneToOneField(Partner, on_delete=models.CASCADE, related_name='coffee')
    city = models.ForeignKey('locations.City', on_delete=models.SET_NULL, null=True, blank=True)
    rating_avg = models.FloatField(default=0.0)

    def __str__(self):
        return f"Coffee: {self.partner.user.username}"

class Agency(models.Model):
    partner = models.OneToOneField(Partner, on_delete=models.CASCADE, related_name='agency')
    rating_avg = models.FloatField(default=0.0)

    def __str__(self):
        return f"Agency: {self.partner.user.username}"
