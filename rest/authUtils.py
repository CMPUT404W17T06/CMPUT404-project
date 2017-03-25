# Author: Braedy Kuzma
from rest_framework import authentication
from rest_framework import exceptions
from ipware.ip import get_ip

from .models import RemoteNode

class nodeToNodeBasicAuth(authentication.BaseAuthentication):
    def authenticate(self, request):
        """
        This is an authentication backend for our rest API. It implements
        HTTP Basic Auth using admin controlled passwords separate from users.
        """
        ip = get_ip(request)
        print('IP:', ip)

        return (None, None)
