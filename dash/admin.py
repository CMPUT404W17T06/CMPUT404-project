from django.contrib import admin
from .models import Post, Comment, Author, Category, CanSee, FriendRequest, \
                    Follow, RemoteCommentAuthor

# Register your models here.

admin.site.register(Author)
admin.site.register(RemoteCommentAuthor)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Category)
admin.site.register(CanSee)
admin.site.register(FriendRequest)
admin.site.register(Follow)
