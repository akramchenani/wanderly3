from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Rating
from .forms import RatingForm
from partners.models import Partner

@login_required
def rate_partner(request, partner_id):
    partner = get_object_or_404(Partner, pk=partner_id, is_approved=True)
    existing = Rating.objects.filter(user=request.user, partner=partner).first()
    if request.method == 'POST':
        form = RatingForm(request.POST, instance=existing)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.user = request.user
            rating.partner = partner
            rating.save()
            # Update avg
            ratings = Rating.objects.filter(partner=partner)
            avg = sum(r.stars for r in ratings) / ratings.count()
            if partner.partner_type == 'hotel' and hasattr(partner, 'hotel'):
                partner.hotel.rating_avg = avg
                partner.hotel.save()
            elif partner.partner_type == 'restaurant' and hasattr(partner, 'restaurant'):
                partner.restaurant.rating_avg = avg
                partner.restaurant.save()
            elif partner.partner_type == 'coffee' and hasattr(partner, 'coffee'):
                partner.coffee.rating_avg = avg
                partner.coffee.save()
            elif partner.partner_type == 'agency' and hasattr(partner, 'agency'):
                partner.agency.rating_avg = avg
                partner.agency.save()
            messages.success(request, 'Rating submitted!')
            return redirect('partners:detail', pk=partner_id)
    else:
        form = RatingForm(instance=existing)
    return render(request, 'reviews/rate.html', {'form': form, 'partner': partner, 'existing': existing})

@login_required
def delete_rating(request, pk):
    rating = get_object_or_404(Rating, pk=pk, user=request.user)
    partner_id = rating.partner.pk
    rating.delete()
    messages.success(request, 'Rating deleted.')
    return redirect('partners:detail', pk=partner_id)
