from django.contrib import admin
from .models import Post, Comment, Author, AuthorFriends, Category
#,FriendRequest
# Register your models here.

admin.site.register(Author)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(AuthorFriends)
admin.site.register(Category)

#admin.site.register(FriendRequest)
