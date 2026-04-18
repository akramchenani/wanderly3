from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm, PartnerRegisterForm, UserUpdateForm, LoginForm
from .models import User

def register_user(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('core:home')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def register_partner(request):
    if request.method == 'POST':
        form = PartnerRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'partner'
            user.save()
            from partners.models import Partner
            partner = Partner.objects.create(
                user=user,
                partner_type=form.cleaned_data['partner_type'],
                phone=form.cleaned_data['phone'],
                description=form.cleaned_data['description'],
                verification_document=form.cleaned_data['verification_document'],
            )
            if partner.partner_type == 'hotel':
                from partners.models import Hotel
                Hotel.objects.create(partner=partner)
            elif partner.partner_type == 'restaurant':
                from partners.models import Restaurant
                Restaurant.objects.create(partner=partner)
            elif partner.partner_type == 'coffee':
                from partners.models import Coffee
                Coffee.objects.create(partner=partner)
            elif partner.partner_type == 'agency':
                from partners.models import Agency
                Agency.objects.create(partner=partner)
            messages.success(request, 'Partner account created! Awaiting admin approval.')
            return redirect('accounts:login')
    else:
        form = PartnerRegisterForm()
    return render(request, 'accounts/register_partner.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(request.GET.get('next', 'core:home'))
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('core:home')

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated!')
            return redirect('accounts:profile')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})
