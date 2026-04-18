from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Partner, Hotel, Restaurant, Coffee, Agency
from locations.models import City

def partner_list(request):
    partner_type = request.GET.get('type', '')
    city_id = request.GET.get('city', '')
    partners = Partner.objects.filter(is_approved=True)
    if partner_type:
        partners = partners.filter(partner_type=partner_type)
    cities = City.objects.all()
    return render(request, 'partners/list.html', {'partners': partners, 'cities': cities, 'partner_type': partner_type})

def partner_detail(request, pk):
    partner = get_object_or_404(Partner, pk=pk, is_approved=True)
    from posts.models import Post
    from reviews.models import Rating
    posts = Post.objects.filter(author=partner.user).order_by('-created_at')
    ratings = Rating.objects.filter(partner=partner)
    user_rating = None
    if request.user.is_authenticated:
        user_rating = ratings.filter(user=request.user).first()
    return render(request, 'partners/detail.html', {
        'partner': partner,
        'posts': posts,
        'ratings': ratings,
        'user_rating': user_rating,
    })

@login_required
def partner_dashboard(request):
    if not hasattr(request.user, 'partner'):
        messages.error(request, 'You are not a partner.')
        return redirect('core:home')
    partner = request.user.partner
    from posts.models import Post
    posts = Post.objects.filter(author=request.user).order_by('-created_at')
    from booking.models import Booking, BookingRequest
    if partner.partner_type == 'hotel':
        bookings = Booking.objects.filter(hotel=partner.hotel).order_by('-created_at')
    else:
        bookings = []
    if partner.partner_type == 'agency':
        requests = BookingRequest.objects.filter(agency=partner.agency).order_by('-created_at')
    else:
        requests = []
    return render(request, 'partners/dashboard.html', {
        'partner': partner,
        'posts': posts,
        'bookings': bookings,
        'requests': requests,
    })

@login_required
def update_partner_profile(request):
    if not hasattr(request.user, 'partner'):
        return redirect('core:home')
    partner = request.user.partner
    if request.method == 'POST':
        partner.phone = request.POST.get('phone', partner.phone)
        partner.description = request.POST.get('description', partner.description)
        if request.FILES.get('profile_photo'):
            partner.profile_photo = request.FILES['profile_photo']
        partner.save()
        # Update city for hotel/restaurant/coffee
        city_id = request.POST.get('city')
        if city_id:
            city = City.objects.filter(pk=city_id).first()
            if partner.partner_type == 'hotel' and hasattr(partner, 'hotel'):
                partner.hotel.city = city
                partner.hotel.save()
            elif partner.partner_type == 'restaurant' and hasattr(partner, 'restaurant'):
                partner.restaurant.city = city
                partner.restaurant.save()
            elif partner.partner_type == 'coffee' and hasattr(partner, 'coffee'):
                partner.coffee.city = city
                partner.coffee.save()
        messages.success(request, 'Profile updated!')
        return redirect('partners:dashboard')
    cities = City.objects.all()
    return render(request, 'partners/update_profile.html', {'partner': partner, 'cities': cities})
