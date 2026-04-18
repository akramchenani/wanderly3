from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('rate/<int:partner_id>/', views.rate_partner, name='rate'),
    path('delete/<int:pk>/', views.delete_rating, name='delete'),
]
