from django import forms
from .models import City, Place

class CityForm(forms.ModelForm):
    class Meta:
        model = City
        fields = ['name', 'description', 'cover_image']

class PlaceForm(forms.ModelForm):
    images = forms.FileField(required=False)

    class Meta:
        model = Place
        fields = ['city', 'name', 'description']
