from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('partner', 'Partner'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    profile_photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True)

    def is_partner_user(self):
        return self.role == 'partner'

    def is_admin_user(self):
        return self.role == 'admin' or self.is_superuser

    def __str__(self):
        return f"{self.username} ({self.role})"
