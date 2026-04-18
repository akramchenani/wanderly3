from django.urls import path
from . import views

app_name = 'flights'

urlpatterns = [
    path('search/', views.search_flights, name='search'),
    path('book/', views.book_flight, name='book'),
    path('my/', views.my_flights, name='my_flights'),
    path('<int:pk>/cancel/', views.cancel_flight, name='cancel'),
]
