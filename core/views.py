from django.shortcuts import render
from django.db.models import Count
from posts.models import Post
from locations.models import City, Place
from partners.models import Partner, Hotel, Restaurant, Agency


def home(request):
    posts  = list(Post.objects.all().order_by('-created_at')[:20])
    cities = list(City.objects.prefetch_related('places').all())

    # Top hotels: approved, ordered by rating then total bookings
    top_hotels = (
        Hotel.objects
        .filter(partner__is_approved=True)
        .select_related('partner__user', 'city')
        .annotate(booking_count=Count('bookings'))
        .order_by('-rating_avg', '-booking_count')[:6]
    )

    # Restaurants for bundles
    restaurants = (
        Restaurant.objects
        .filter(partner__is_approved=True)
        .select_related('partner__user', 'city')
        .order_by('-rating_avg')[:12]
    )

    # Agencies for bundles
    agencies = (
        Agency.objects
        .filter(partner__is_approved=True)
        .select_related('partner__user')
        .order_by('-rating_avg')[:6]
    )

    featured_partners = (
        Partner.objects.filter(is_approved=True).order_by('?')[:6]
    )

    return render(request, 'core/home.html', {
        'posts':              posts,
        'cities':             cities,
        'top_hotels':         top_hotels,
        'restaurants':        restaurants,
        'agencies':           agencies,
        'featured_partners':  featured_partners,
    })


def about(request):
    return render(request, 'core/about.html')


def search(request):
    q = request.GET.get('q', '')
    posts    = Post.objects.filter(title__icontains=q)    if q else Post.objects.none()
    cities   = City.objects.filter(name__icontains=q)     if q else City.objects.none()
    partners = Partner.objects.filter(
        is_approved=True, user__username__icontains=q
    ) if q else Partner.objects.none()
    return render(request, 'core/search.html', {
        'q': q, 'posts': posts, 'cities': cities, 'partners': partners
    })
