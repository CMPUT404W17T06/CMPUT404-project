# Author: Braedy Kuzma

from django.db import models
from django.conf import settings
import django.utils.timezone as timezone
import uuid

class Author(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    url = models.URLField()
    host = models.URLField()
    def __str__(self):
        return self.displayName

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
        name = author.user.get_username()
        return '{} - {}'.format(name, friend)

class Post(models.Model):
    class Meta:
        ordering = ['published']
    title = models.CharField(max_length=32)
    source = models.URLField() # not sure what the difference is between these
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
    visibleTo = models.ManyToManyField(Author,
                                       related_name='visibleTo',
                                       blank=True)
    unlisted = models.BooleanField(default=False)

    def __str__(self):
        return '"{}" - {}'.format(self.title, self.author.get_username())

class Category(models.Model):
    """
    Another container class, this one for post categories. This might be better
    off as a many-to-many relationship.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.CharField(max_length=32)

    def __str__(self):
        return '{} - {}'.format(post.title, category)

class Comment(models.Model):
    class Meta:
        ordering = ['published']
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               related_name='comment_author')
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment = models.TextField()
    contentType = models.CharField(max_length=32)
    published = models.DateTimeField(default=timezone.now)

    # This should really have a validator
    id = models.CharField('id', max_length=36, default=uuid.uuid4,
                          primary_key=True)

    def __str__(self):
        return '"{}" - {}'.format(self.post.title,
                                  self.author.get_username())

#Larin
# need to create author class first
"""class FriendRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    requester = models.ForeignKey(Author, related_name="requester") #iniated the friend request
    requestee = models.ForeignKey(Author, related_name="requestee") #received the friend request
    accepted = models.NullBooleanField(blank=True, null=True, default=None) #was the friend request accepted or rejected? if null means request is pending
    created = models.DateTimeField(auto_now=True) #when was the request created"""
