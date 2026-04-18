from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    images = forms.FileField(required=False)

    class Meta:
        model = Post
        fields = ['title', 'description', 'post_type', 'city', 'price']

class CommentForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), max_length=500)
