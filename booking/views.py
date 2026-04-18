from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Booking, BookingRequest
from .forms import BookingForm, BookingRequestForm
from partners.models import Hotel, Agency
from posts.models import Post
from notifications.models import Notification


@login_required
def book_hotel(request, hotel_id, post_id=None):
    hotel = get_object_or_404(Hotel, pk=hotel_id, partner__is_approved=True)
    room_post = None
    if post_id:
        room_post = get_object_or_404(Post, pk=post_id)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.hotel = hotel
            booking.room_post = room_post
            nights = (booking.check_out - booking.check_in).days
            if room_post and room_post.price:
                booking.total_price = room_post.price * nights
            # Always save as pending — payment page will confirm
            booking.status = 'pending'
            booking.save()
            Notification.objects.create(
                user=hotel.partner.user,
                notif_type='booking',
                content=f'New booking from {request.user.username}!'
            )
            # Redirect to payment simulation page
            return redirect('booking:payment', pk=booking.pk)
    else:
        form = BookingForm()

    return render(request, 'booking/book_hotel.html', {
        'form': form, 'hotel': hotel, 'room_post': room_post
    })


@login_required
def payment(request, pk):
    """Simulated payment page — no real charge."""
    booking = get_object_or_404(Booking, pk=pk, user=request.user)

    if request.method == 'POST':
        # Simulation: just mark as confirmed
        booking.status = 'confirmed'
        booking.save()
        Notification.objects.create(
            user=booking.hotel.partner.user,
            notif_type='booking',
            content=f'Payment received for booking #{booking.pk} from {request.user.username}!'
        )
        return render(request, 'booking/payment.html', {
            'booking': booking,
            'payment_accepted': True,
        })

    return render(request, 'booking/payment.html', {
        'booking': booking,
        'payment_accepted': False,
    })


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    requests = BookingRequest.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'booking/my_bookings.html', {
        'bookings': bookings, 'requests': requests
    })


@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if booking.status in ['pending', 'confirmed']:
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Booking cancelled.')
    return redirect('booking:my_bookings')


@login_required
def request_agency(request, agency_id):
    agency = get_object_or_404(Agency, pk=agency_id, partner__is_approved=True)
    if request.method == 'POST':
        form = BookingRequestForm(request.POST)
        if form.is_valid():
            req = form.save(commit=False)
            req.user = request.user
            req.agency = agency
            req.save()
            Notification.objects.create(
                user=agency.partner.user,
                notif_type='booking',
                content=f'New agency request from {request.user.username}!'
            )
            messages.success(request, 'Request sent to agency!')
            return redirect('booking:my_bookings')
    else:
        form = BookingRequestForm()
    return render(request, 'booking/request_agency.html', {'form': form, 'agency': agency})


@login_required
def update_booking_status(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if not hasattr(request.user, 'partner'):
        return redirect('core:home')
    new_status = request.POST.get('status')
    if new_status in ['confirmed', 'cancelled', 'completed']:
        booking.status = new_status
        booking.save()
        Notification.objects.create(
            user=booking.user,
            notif_type='booking',
            content=f'Your booking #{booking.pk} is now {new_status}.'
        )
    return redirect('partners:dashboard')


@login_required
def update_request_status(request, pk):
    req = get_object_or_404(BookingRequest, pk=pk)
    if not hasattr(request.user, 'partner'):
        return redirect('core:home')
    new_status = request.POST.get('status')
    if new_status in ['accepted', 'rejected']:
        req.status = new_status
        req.save()
        Notification.objects.create(
            user=req.user,
            notif_type='booking',
            content=f'Your agency request #{req.pk} was {new_status}.'
        )
    return redirect('partners:dashboard')
