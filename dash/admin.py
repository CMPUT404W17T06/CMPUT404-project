from django.contrib import admin
from .models import Post, Comment, Author, AuthorFriends, Category, CanSee,FriendRequest, Nodes
# Register your models here.

admin.site.register(Author)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(AuthorFriends)
admin.site.register(Category)
admin.site.register(CanSee)
admin.site.register(FriendRequest)
admin.site.register(Nodes)