# Author: Braedy Kuzma
import base64
from urllib.parse import urlsplit
from pprint import pprint # TODO stop logging accesses

from django.http import HttpResponse
from rest_framework import authentication
from rest_framework import exceptions

from .models import LocalCredentials, RemoteCredentials

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

def getRemoteCredentials(url):
    """
    Finds a remote host that can be used for the given url.
    Returns None if it couldn't find.
    """
    hostSplit = urlsplit(url)
    hostNetloc = hostSplit.netloc
    for remoteHost in RemoteCredentials.objects.all():
        remoteHostSplit = urlsplit(remoteHost.host)
        remoteHostNetloc = remoteHostSplit.netloc
        if hostNetloc == remoteHostNetloc:
            return remoteHost

    return None


class nodeToNodeBasicAuth(authentication.BaseAuthentication):
    def authenticate(self, request):
        """
        This is an authentication backend for our rest API. It implements
        HTTP Basic Auth using admin controlled passwords separate from users.
        """
        # TODO stop logging accesses
        print(request.method, request.path)
        body = request.body.decode('utf-8')
        pprint(body)

        # Didn't provide auth
        print('HTTP_AUTHORIZATION' in request.META)
        if 'HTTP_AUTHORIZATION' not in request.META:
            raise exceptions.AuthenticationFailed()

        auth = request.META['HTTP_AUTHORIZATION']
        print('AUTH', auth)

        # Tried to auth the wrong way
        prefix = 'Basic '
        if not auth.startswith(prefix):
            raise exceptions.AuthenticationFailed()

        # Get username and password
        token = auth[len(prefix):]
        username, password = parseBasicAuthToken(token)

        # TODO stop logging accesses
        print('AUTHD WITH: {}, {}\n\n'.format(username, password))

        # Fail if these credentials don't exist
        try:
            creds = LocalCredentials.objects.get(username=username)
        except LocalCredentials.DoesNotExist:
            raise exceptions.AuthenticationFailed()

        # We should probably check their password matches
        if creds.password != password:
            raise exceptions.AuthenticationFailed()

        # These are useful things for auth.. maybe later
        return (None, None)

    def authenticate_header(self, request):
        return 'Basic realm="api"'
