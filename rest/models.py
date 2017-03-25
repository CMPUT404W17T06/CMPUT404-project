from django.db import models

# Create your models here.

class RemoteNode(models.Model):
    url = models.URLField(unique=True)

    # Password and username remote node needs to provide to auth with us
    remoteToLocalUsername = models.CharField(max_length=64)
    remoteToLocalPassword = models.CharField(max_length=64)

    # Password and username we need to provide to remote to auth with them
    localToRemoteUserName = models.CharField(max_length=64)
    localToRemotePassword = models.CharField(max_length=64)

    def __str__(self):
        return self.url
