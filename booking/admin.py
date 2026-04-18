from django.contrib import admin
from .models import Booking, BookingRequest

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['pk', 'user', 'hotel', 'check_in', 'check_out', 'status', 'payment_method']
    list_filter = ['status', 'payment_method']

@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = ['pk', 'user', 'agency', 'status']
    list_filter = ['status']
