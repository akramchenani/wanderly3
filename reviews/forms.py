from django import forms
from .models import Rating

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['stars', 'comment']
        widgets = {
            'stars': forms.RadioSelect(choices=[(i, f'{i} ★') for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 3}),
        }
