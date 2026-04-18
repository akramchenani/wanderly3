from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('partners/', include('partners.urls')),
    path('locations/', include('locations.urls')),
    path('posts/', include('posts.urls')),
    path('booking/', include('booking.urls')),
    path('flights/', include('flights.urls')),
    path('chat/', include('chat.urls')),
    path('notifications/', include('notifications.urls')),
    path('reviews/', include('reviews.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
