from django import forms
from .models import Booking, BookingRequest

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['check_in', 'check_out', 'guests', 'payment_method']
        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date'}),
            'check_out': forms.DateInput(attrs={'type': 'date'}),
        }

class BookingRequestForm(forms.ModelForm):
    class Meta:
        model = BookingRequest
        fields = ['details', 'related_hotel']
