from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('register/partner/', views.register_partner, name='register_partner'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
]
