from django.urls import path
from . import views

app_name = 'locations'

urlpatterns = [
    path('', views.city_list, name='city_list'),
    path('<int:pk>/', views.city_detail, name='city_detail'),
    path('place/<int:pk>/', views.place_detail, name='place_detail'),
]
