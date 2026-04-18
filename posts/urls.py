from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.post_list, name='list'),
    path('<int:pk>/', views.post_detail, name='detail'),
    path('create/', views.create_post, name='create'),
    path('<int:pk>/edit/', views.edit_post, name='edit'),
    path('<int:pk>/delete/', views.delete_post, name='delete'),
    path('<int:pk>/like/', views.toggle_like, name='like'),
    path('<int:pk>/comment/', views.add_comment, name='comment'),
    path('comment/<int:pk>/delete/', views.delete_comment, name='delete_comment'),
]
