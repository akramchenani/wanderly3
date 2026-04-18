from django.db import models
from accounts.models import User

class Flight(models.Model):
    TYPE_CHOICES = [
        ('one_way', 'One Way'),
        ('round_trip', 'Round Trip'),
    ]
    STATUS_CHOICES = [
        ('booked', 'Booked'),
        ('cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='flights')
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    flight_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='one_way')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    airline = models.CharField(max_length=100, blank=True)
    flight_number = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='booked')
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.origin} → {self.destination} ({self.departure_date})"
