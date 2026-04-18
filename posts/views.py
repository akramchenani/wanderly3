from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from .models import Post, PostImage, Comment, Like
from .forms import PostForm, CommentForm
from locations.models import City

def post_list(request):
    posts = Post.objects.all().order_by('-created_at')
    city_id = request.GET.get('city')
    post_type = request.GET.get('type')
    search = request.GET.get('q')
    if city_id:
        posts = posts.filter(city_id=city_id)
    if post_type:
        posts = posts.filter(post_type=post_type)
    if search:
        posts = posts.filter(title__icontains=search)
    cities = City.objects.all()
    from django.core.paginator import Paginator
    paginator = Paginator(posts, 20)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    return render(request, 'posts/list.html', {'posts': posts, 'cities': cities})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comment_form = CommentForm()
    user_comment = None
    user_liked = False
    if request.user.is_authenticated:
        user_comment = Comment.objects.filter(user=request.user, post=post).first()
        user_liked = Like.objects.filter(user=request.user, post=post).exists()
    return render(request, 'posts/detail.html', {
        'post': post,
        'comment_form': comment_form,
        'user_comment': user_comment,
        'user_liked': user_liked,
    })

@login_required
def create_post(request):
    partner = getattr(request.user, 'partner', None)
    if not partner or not partner.is_approved:
        messages.error(request, 'Only approved partners can create posts.')
        return redirect('posts:list')
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            # Enforce post limit
            current_count = Post.objects.filter(author=request.user).count()
            if current_count >= settings.POST_LIMIT_PER_PARTNER and partner.partner_type != 'agency':
                # Delete oldest post
                oldest = Post.objects.filter(author=request.user).order_by('created_at').first()
                if oldest:
                    oldest.delete()
                messages.warning(request, 'Post limit reached. Your oldest post was replaced.')
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            images = request.FILES.getlist('images')
            for i, img in enumerate(images[:settings.MAX_IMAGES_PER_POST]):
                PostImage.objects.create(post=post, image=img)
            messages.success(request, 'Post created!')
            return redirect('posts:detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'posts/form.html', {'form': form, 'action': 'Create'})

@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()
            images = request.FILES.getlist('images')
            current_count = post.images.count()
            for img in images[:settings.MAX_IMAGES_PER_POST - current_count]:
                PostImage.objects.create(post=post, image=img)
            messages.success(request, 'Post updated!')
            return redirect('posts:detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'posts/form.html', {'form': form, 'action': 'Edit', 'post': post})

@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted.')
        return redirect('posts:list')
    return render(request, 'posts/confirm_delete.html', {'post': post})

@login_required
def toggle_like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    return JsonResponse({'liked': liked, 'count': post.like_count()})

@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if Comment.objects.filter(user=request.user, post=post).exists():
        messages.error(request, 'You already commented on this post.')
        return redirect('posts:detail', pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            Comment.objects.create(user=request.user, post=post, content=form.cleaned_data['content'])
            messages.success(request, 'Comment added!')
    return redirect('posts:detail', pk=pk)

@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk, user=request.user)
    post_pk = comment.post.pk
    comment.delete()
    return redirect('posts:detail', pk=post_pk)
