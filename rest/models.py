from django.db import models

# Create your models here.

class RemoteCredentials(models.Model):
    """
    Credentials to use for a remote server.
    """
    class Meta:
        verbose_name_plural = 'RemoteCredentials'
        unique_together = ('host', 'username')

    # The url of the remote server that we should use the below credentials for
    host = models.URLField()

    # Password and username to use with the remote server
    username = models.CharField(max_length=64)
    password = models.CharField(max_length=64)

    def __str__(self):
        return '{}@{}'.format(self.username, self.host)

class LocalCredentials(models.Model):
    """
    Credentials for a remote server to use when requesting things for us.

    Because we can't tell where the request is coming from (even if we get the
    ip we can't tell which host it's from), we check incoming auth with any of
    these objects. Note that username is unique so .get(username=name) should
    always succeed with one object or fail.
    """
    class Meta:
        verbose_name_plural = 'LocalCredentials'

    # This field should be a description of these credentials (Ideally which
    # host we would be using this with)
    description = models.CharField(max_length=256)

    # Password and username a remote server can use with us
    username = models.CharField(max_length=64, unique=True)
    password = models.CharField(max_length=64)

    def __str__(self):
        return self.description
