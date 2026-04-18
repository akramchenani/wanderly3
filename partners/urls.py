from django.urls import path
from . import views

app_name = 'partners'

urlpatterns = [
    path('', views.partner_list, name='list'),
    path('<int:pk>/', views.partner_detail, name='detail'),
    path('dashboard/', views.partner_dashboard, name='dashboard'),
    path('profile/update/', views.update_partner_profile, name='update_profile'),
]
