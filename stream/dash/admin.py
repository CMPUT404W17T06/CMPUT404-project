from django.contrib import admin
from .models import Post, Comment, AuthorFriends, Category#,FriendRequest
# Register your models here.

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(AuthorFriends)
admin.site.register(Category)

#admin.site.register(FriendRequest)
