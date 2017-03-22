# Author: Braedy Kuzma

from django.db import models
from django.conf import settings
import django.utils.timezone as timezone
from django.core.exceptions import ValidationError
import uuid


class Author(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    url = models.URLField()
    host = models.URLField()
    github = models.URLField(blank=True, default='')
    bio = models.TextField(blank=True, default='')

    # http://hostname/author/<uuid>
    id = models.URLField(primary_key=True)

    def __str__(self):
        return self.user.get_username()

class AuthorFriend(models.Model):
    """
    This class is just a container for a FRIENDSHIP (url). It simulates a
    many-to-one relationship for Authors. Finding the list of friendships is
    easy, just join the list of friends. This might be better off as a
    many-to-many relationship.
    """
    friendId = models.URLField()
    host = models.URLField()
    displayName = models.CharField(max_length=64)
    friend1=models.ForeignKey(Author,on_delete=models.CASCADE,related_name = "friend1")
    friend2=models.ForeignKey(Author,on_delete=models.CASCADE,related_name = "friend2")
    
    def __str__(self):
        return '{} and {}'.format(self.friend1.user.get_username(),self.friend2.user.get_username())  

class Post(models.Model):
    class Meta:
        ordering = ['-published']
    title = models.CharField(max_length=32)
    description = models.CharField(max_length=140) # why not Twitter?
    contentType = models.CharField(max_length=32)
    content = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE,
                               related_name='post_author')
    published = models.DateTimeField(default=timezone.now)

    # http://hostname/posts/<uuid>
    id = models.URLField(primary_key=True)
    visibility = models.CharField(max_length=10, default="PUBLIC")
    unlisted = models.BooleanField(default=False)

    def __str__(self):
        return '"{}" - {}'.format(self.title, self.author.user.get_username())

    def clean():
        """
        Custom validation.
        - Ensure visibility == PRIVATE if there's visibleTos
        """
        if visiblity != 'PRIVATE' and self.cansee_set.count() != 0:
            raise ValidationError('Visibilty must be private if visibileTo is'
                                  ' set')

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
    visibleTo = models.URLField() # This is an author id, could be remote

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

    # The only id field that's a uuid because there's no way to directly access
    # a comment via URI
    # So says the Hindle
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    def __str__(self):
        return '{} on "{}"'.format(self.author.user.get_username(),
                                   self.post.title)

class Follow(models.Model):
    follower = models.ForeignKey(Author, related_name = "follower")
    followee = models.ForeignKey(Author, related_name = "followee")
    bidirectional = models.BooleanField(default=False)
    reject = models.BooleanField(default=False)

    def __str__(self):
        a = self.followee.user.get_username()
        
        return '{} -> {}'.format(self.follower.user.get_username(),self.followee.user.get_username())
    def save(self):        
        if (Follow.objects.filter(follower = self.followee,followee = self.follower).count())==1:
    
            self.bidirectional = True
            obj =Follow.objects.get(follower=self.followee,followee=self.follower)
            obj.bidirectional=True
            obj.save()
            if  (AuthorFriend.objects.filter(friend1 = self.followee,friend2=self.follower).count()+
            AuthorFriend.objects.filter(friend1 = self.follower,friend2=self.followee).count())<1:
                friend = AuthorFriend(friend1 = self.followee, friend2 = self.follower)
                friend.save()
            
            super(Follow,self).save()
            #obj.save()
            print(Follow.objects.get(follower=self.followee,followee=self.follower).bidirectional)
        else:

            super(Follow, self).save()
