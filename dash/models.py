# Author: Braedy Kuzma

from django.db import models
from django.conf import settings
import django.utils.timezone as timezone
import uuid
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User

class Author(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    id = models.CharField('id', max_length=36, primary_key=True, default=uuid.uuid4)
    url = models.URLField()
    host = models.URLField()
    github = models.URLField(default='', blank=True)
    displayName = models.CharField(max_length=50, null=True, blank=True, default='') 
    email = models.EmailField(max_length=254, default="" , null=True, blank=True)
    firstName = models.CharField(max_length=30, default="" , null=True, blank=True)
    lastName = models.CharField(max_length=30, default="", null=True, blank=True)
    bio = models.TextField(default="", null=True, blank=True)
    friends = models.ManyToManyField("self", related_name="friends", blank=True)

    def __str__(self):
        return self.user.get_username()
class AuthorFriends(models.Model):
    """
    This class is just a container for a FRIENDSHIP (url). It simulates a
    many-to-one relationship for Authors. Finding the list of friendships is
    easy, just join the list of friends. This might be better off as a
    many-to-many relationship.
    """
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    friendId = models.CharField(max_length=36)
    host = models.URLField()
    displayName = models.CharField(max_length=64)

    def __str__(self):
        name = self.author.user.get_username()
        return '{} -> {}'.format(name, self.displayName)

class Post(models.Model):
    class Meta:
        ordering = ['-published']
    title = models.CharField(max_length=32)
    origin = models.URLField()
    description = models.CharField(max_length=140) # why not Twitter?
    contentType = models.CharField(max_length=32)
    content = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE,
                               related_name='post_author')
    published = models.DateTimeField(default=timezone.now)

    # This should really have a validator
    id = models.CharField('id', max_length=36, default=uuid.uuid4,
                          primary_key=True)
    visibility = models.CharField(max_length=10, default="PUBLIC")
    unlisted = models.BooleanField(default=False)

    def __str__(self):
        return '"{}" - {}'.format(self.title, self.author.user.get_username())

class Category(models.Model):
    """
    Another container class, this one for post categories. This might be better
    off as a many-to-many relationship.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.CharField(max_length=32)

    def __str__(self):
        return '"{}" in {}'.format(self.post.title, self.category)

class CanSee(models.Model):
    """
    Another container class, this one for users who can see private posts.  This
     might be better off as a many-to-many relationship.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    visibleTo = models.URLField()

    def __str__(self):
        return '{} sees {}'.format(self.visibleTo, self.post)

class Comment(models.Model):
    class Meta:
        ordering = ['published']
    author = models.ForeignKey(Author, on_delete=models.CASCADE,
                               related_name='comment_author')
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment = models.TextField()
    contentType = models.CharField(max_length=32)
    published = models.DateTimeField(default=timezone.now)

    # This should really have a validator
    id = models.CharField('id', max_length=36, default=uuid.uuid4,
                          primary_key=True)

    def __str__(self):
        return '{} on "{}"'.format(self.author.user.get_username(),
                                   self.post.title)

class FriendRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    requester = models.ForeignKey(Author, related_name="requester") #iniated the friend request
    requestee = models.ForeignKey(Author, related_name="requestee") #received the friend request
    accepted = models.NullBooleanField(blank=True, null=True, default=None) #was the friend request accepted or rejected? if null means request is pending
    created = models.DateTimeField(auto_now=True) #when was the request created
