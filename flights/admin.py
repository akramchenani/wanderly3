from django.contrib import admin
from .models import Flight

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ['user', 'origin', 'destination', 'departure_date', 'status', 'booked_at']
    list_filter = ['status', 'flight_type']
