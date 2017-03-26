# Author: Braedy Kuzma

from django.db import models
from django.conf import settings
import django.utils.timezone as timezone
from django.core.exceptions import ValidationError
import uuid


class Author(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    url = models.URLField()
    host = models.URLField()
    github = models.URLField(blank=True, default='')
    bio = models.TextField(blank=True, default='')

    # http://hostname/author/<uuid>
    id = models.URLField(primary_key=True)

    def __str__(self):
        return self.user.get_username()

class Follow(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE,
                               related_name='follow')
    friend = models.URLField()

    def __str__(self):
        return '{} follows {}'.format(self.author, self.friend)

class FriendRequest(models.Model):
    requester =  models.URLField()
    requestee = models.ForeignKey(Author, on_delete=models.CASCADE,
                                  related_name='request')
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} for {}'.format(self.requester, self.requestee)

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

class RemoteCommentAuthor(models.Model):
    """
    We need to cache remote comment authors. I think this is a terrible idea and
    we should do it better but right now fuck it. And probably until the end
    of time.
    """
    authorId = models.URLField(primary_key=True)
    host = models.URLField()
    displayName = models.CharField(max_length=256)
    github = models.URLField(blank=True, default='')

    def __str__(self):
        return '{}@{}'.format(self.displayName, self.authorId)

class Comment(models.Model):
    class Meta:
        ordering = ['published']
    # As it stands, this could be a remote user. We're currently sent info about
    # this user but we are not going to store it and will request it from the
    # remote server every time. We could start caching stuff later.
    author = models.URLField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment = models.TextField()
    contentType = models.CharField(max_length=32)
    published = models.DateTimeField(default=timezone.now)

    # The only id field that's a uuid because there's no way to directly access
    # a comment via URI
    # So says the Hindle
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    def __str__(self):
        try:
            localAuthor = Author.objects.get(id=self.author)
            name = localAuthor.user.get_username()
        except Author.DoesNotExist:
            name = "Remote user"

        return '{} on "{}"'.format(name,
                                   self.post.title)
