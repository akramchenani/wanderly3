from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import redirect
from .models import City, Place, PlaceImage
from django.conf import settings
import urllib.request
import json

def city_list(request):
    cities = City.objects.all()
    return render(request, 'locations/city_list.html', {'cities': cities})

def city_detail(request, pk):
    city = get_object_or_404(City, pk=pk)
    places = city.places.all()[:20]
    from posts.models import Post
    posts = Post.objects.filter(city=city).order_by('-created_at')[:20]
    partners = []
    from partners.models import Hotel, Restaurant, Coffee
    hotels = Hotel.objects.filter(city=city, partner__is_approved=True)
    restaurants = Restaurant.objects.filter(city=city, partner__is_approved=True)
    coffees = Coffee.objects.filter(city=city, partner__is_approved=True)
    # Weather
    weather = None
    api_key = settings.WEATHER_API_KEY
    if api_key and api_key != 'your_openweathermap_api_key':
        try:
            url = f"{settings.WEATHER_API_URL}?q={city.name}&appid={api_key}&units=metric"
            with urllib.request.urlopen(url, timeout=3) as resp:
                weather = json.loads(resp.read())
        except Exception:
            weather = None
    return render(request, 'locations/city_detail.html', {
        'city': city,
        'places': places,
        'posts': posts,
        'hotels': hotels,
        'restaurants': restaurants,
        'coffees': coffees,
        'weather': weather,
    })

def place_detail(request, pk):
    place = get_object_or_404(Place, pk=pk)
    return render(request, 'locations/place_detail.html', {'place': place})
