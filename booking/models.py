from django.db import models
from accounts.models import User
from partners.models import Hotel, Agency
from posts.models import Post

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    PAYMENT_CHOICES = [
        ('card', 'Credit Card'),
        ('cash', 'Cash on Arrival'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='bookings')
    room_post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True, blank=True)
    check_in = models.DateField()
    check_out = models.DateField()
    guests = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='card')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking {self.pk} - {self.user.username} at {self.hotel}"

    def nights(self):
        return (self.check_out - self.check_in).days

class BookingRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='booking_requests')
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='booking_requests')
    related_hotel = models.ForeignKey(Hotel, on_delete=models.SET_NULL, null=True, blank=True)
    details = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request {self.pk} - {self.user.username} to {self.agency}"
