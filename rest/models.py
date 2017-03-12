from django.db import models

# Create your models here.

class RemoteNode(models.Model):
    url = models.URLField()

    # Password and username remote node needs to provide to auth with us
    remoteToLocalUsername = models.TextField()
    remoteToLocalPassword = models.TextField()

    # Password and username we need to provide to remote to auth with them
    localToRemoteUserName = models.TextField()
    localToRemotePassword = models.TextField()

    def __str__(self):
        return self.url
