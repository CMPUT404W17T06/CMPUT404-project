from django.contrib import admin
from .models import Post, Comment, Author, AuthorFriend, Category, CanSee, \
                    Follow
# Register your models here.

admin.site.register(Author)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(AuthorFriend)
admin.site.register(Category)
admin.site.register(CanSee)
admin.site.register(Follow)
