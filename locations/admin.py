from django.contrib import admin
from .models import City, Place, PlaceImage
from django.conf import settings

class PlaceImageInline(admin.TabularInline):
    model = PlaceImage
    max_num = 5
    extra = 1

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'city']
    list_filter = ['city']
    inlines = [PlaceImageInline]

    def save_model(self, request, obj, form, change):
        city = obj.city
        if not change:
            count = Place.objects.filter(city=city).count()
            if count >= settings.MAX_PLACES_PER_CITY:
                from django.contrib import messages
                self.message_user(request, f'Max {settings.MAX_PLACES_PER_CITY} places per city reached.', messages.ERROR)
                return
        super().save_model(request, obj, form, change)
