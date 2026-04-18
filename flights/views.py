from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Flight
from .forms import FlightSearchForm
import json

def mock_flight_search(origin, destination, date, flight_type):
    """Simulate flight results when no API key is configured."""
    import random
    airlines = ['Air Algeria', 'Air France', 'Turkish Airlines', 'Emirates', 'Lufthansa']
    results = []
    for i in range(5):
        results.append({
            'airline': random.choice(airlines),
            'flight_number': f'FL{random.randint(100, 999)}',
            'origin': origin,
            'destination': destination,
            'departure_date': str(date),
            'price': round(random.uniform(150, 900), 2),
            'duration': f'{random.randint(2, 12)}h {random.randint(0, 59)}m',
        })
    return results

@login_required
def search_flights(request):
    results = []
    form = FlightSearchForm(request.GET or None)
    if request.GET and form.is_valid():
        origin = form.cleaned_data['origin']
        destination = form.cleaned_data['destination']
        date = form.cleaned_data['departure_date']
        flight_type = form.cleaned_data['flight_type']
        results = mock_flight_search(origin, destination, date, flight_type)
        request.session['flight_search'] = {
            'origin': origin,
            'destination': destination,
            'date': str(date),
            'flight_type': flight_type,
        }
    return render(request, 'flights/search.html', {'form': form, 'results': results})

@login_required
def book_flight(request):
    if request.method == 'POST':
        search = request.session.get('flight_search', {})
        flight = Flight.objects.create(
            user=request.user,
            origin=search.get('origin', ''),
            destination=search.get('destination', ''),
            departure_date=search.get('date'),
            flight_type=search.get('flight_type', 'one_way'),
            airline=request.POST.get('airline', ''),
            flight_number=request.POST.get('flight_number', ''),
            price=request.POST.get('price', 0),
        )
        messages.success(request, f'Flight {flight.flight_number} booked successfully!')
        return redirect('flights:my_flights')
    return redirect('flights:search')

@login_required
def my_flights(request):
    flights = Flight.objects.filter(user=request.user).order_by('-booked_at')
    return render(request, 'flights/my_flights.html', {'flights': flights})

@login_required
def cancel_flight(request, pk):
    flight = get_object_or_404(Flight, pk=pk, user=request.user)
    flight.status = 'cancelled'
    flight.save()
    messages.success(request, 'Flight cancelled.')
    return redirect('flights:my_flights')
