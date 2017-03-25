# Author: Braedy Kuzma
import base64

from django.http import HttpResponse
from rest_framework import authentication
from rest_framework import exceptions
from ipware.ip import get_ip

def createBasicAuthToken(username, password):
    """
    This creates an HTTP Basic Auth token from a username and password.
    """
    # Format into the HTTP Basic Auth format
    tokenString = '{}:{}'.format(username, password)

    # Encode into bytes for b64, then into b64
    bytesString = tokenString.encode('utf-8')
    return base64.b64encode(bytesString)

def parseBasicAuthToken(token):
    """
    This parses an HTTP Basic Auth token and returns a tuple of (username,
    password).
    """
    # Convert the token into a bytes object so b64 can work with it
    if isinstance(token, str):
        token = token.encode('utf-8')

    # Decode from b64 then bytes
    parsedBytes = base64.b64decode(token)
    parsedString = parsedBytes.decode('utf-8')

    # Split out the username, rejoin the password if it had colons
    username, *passwordParts = parsedString.split(':')
    password = ':'.join(passwordParts)

    return (username, password)

class nodeToNodeBasicAuth(authentication.BaseAuthentication):
    def authenticate(self, request):
        """
        This is an authentication backend for our rest API. It implements
        HTTP Basic Auth using admin controlled passwords separate from users.
        """
        if 'HTTP_AUTHORIZATION' not in request.META:
            raise exceptions.AuthenticationFailed()



        return (None, None)

    def authenticate_header(self, request):
        return 'Basic realm="api"'
