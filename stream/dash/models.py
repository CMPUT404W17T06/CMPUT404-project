# Author: Braedy Kuzma

from django.db import models
from django.conf import settings
import django.utils.timezone as timezone
import uuid

"""class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    displayName = models.CharField(max_length=50, null=True, blank=True, default='')
    firstName = models.CharField(max_length=30, default="" , null=True, blank=True)
    lastName = models.CharField(max_length=30, default="", null=True, blank=True)
    url = models.CharField(max_length=500, null=True, blank=True )
    github = models.CharField(max_length=500, null=True, blank=True)
    email = models.EmailField(max_length=254, default="" , null=True, blank=True)
    description = models.TextField(default="", null=True, blank=True)
    friends = models.ManyToManyField("self", related_name="friends", blank=True)
    def __str__(self):
        return self.displayName"""

class Post(models.Model):
    title = models.CharField(max_length=32)
    source = models.CharField(max_length=128)
    origin = models.CharField(max_length=128)
    description = models.CharField(max_length=140) # why not Twitter?
    contentType = models.CharField(max_length=32)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               null=True, # Lets the key be null
                               on_delete=models.SET_NULL, # TODO is this what we want
                               related_name='post_author')
    categories = models.CharField(max_length=128)
    published = models.DateTimeField(default=timezone.now)

    # This should really have a validator
    id = models.CharField('id', max_length=36, default=uuid.uuid4,
                          primary_key=True)
    visibility = models.CharField(max_length=10, default="PUBLIC")
    visibleTo = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                       related_name='visibleTo',
                                       blank=True)
    unlisted = models.BooleanField(default=False)

    def __str__(self):
        return '"{}" - {}'.format(self.title, self.author.get_username())

class Comment(models.Model):
    class Meta:
        ordering = ['published']
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               null=True, # Lets the key be null
                               on_delete=models.SET_NULL, # TODO is this what we want
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
