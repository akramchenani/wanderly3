from django.contrib import admin
from .models import Post, PostImage, Comment, Like

class PostImageInline(admin.TabularInline):
    model = PostImage
    max_num = 5

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'post_type', 'city', 'created_at']
    list_filter = ['post_type', 'city']
    inlines = [PostImageInline]

admin.site.register(Comment)
admin.site.register(Like)
