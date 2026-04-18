from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

class PartnerRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    verification_document = forms.FileField(required=True)
    partner_type = forms.ChoiceField(choices=[
        ('hotel', 'Hotel'),
        ('restaurant', 'Restaurant'),
        ('coffee', 'Coffee'),
        ('agency', 'Agency'),
    ])
    phone = forms.CharField(max_length=20)
    description = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'bio', 'profile_photo']

class LoginForm(AuthenticationForm):
    pass
