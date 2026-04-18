from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    path('hotel/<int:hotel_id>/',                    views.book_hotel,             name='book_hotel'),
    path('hotel/<int:hotel_id>/room/<int:post_id>/', views.book_hotel,             name='book_hotel_room'),
    path('payment/<int:pk>/',                        views.payment,                name='payment'),
    path('my/',                                      views.my_bookings,            name='my_bookings'),
    path('<int:pk>/cancel/',                         views.cancel_booking,         name='cancel'),
    path('agency/<int:agency_id>/',                  views.request_agency,         name='request_agency'),
    path('status/<int:pk>/',                         views.update_booking_status,  name='update_status'),
    path('request/status/<int:pk>/',                 views.update_request_status,  name='update_request_status'),
]
