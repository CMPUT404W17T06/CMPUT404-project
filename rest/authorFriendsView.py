from rest_framework.views import APIView

from dash.models import Follow
from .serializers import AuthorSerializer
from .dataUtils import getAuthor
from .httpUtils import JSONResponse

class AuthorFriendsView(APIView):
    """
    This view gets a list of an author's friends.
    """
    def get(self, request, aid):
        author = getAuthor(request, aid)

        # Start data response
        data = {}
        data['query']  = 'friends'

        # Get list of friends
        urls = []
        for follow in author.follow.all():
            urls.append(follow.friend)
        data['authors'] = urls

        return JSONResponse(data)

class AuthorIsFriendsView(APIView):
    """
    This view gets whether or not this user is friends with another.
    """
    def get(self, request, aid=None, other=None):
        """
        This checks if the author at aid is friends with the author that has aid
        than other.
        """
        author = getAuthor(request, aid)

        # Make http id, and https id for back up
        otherId = 'http://' + other
        otherIdHttps = 'https://' + other

        # Get the following relationship
        follows = Follow.objects.filter(author=author, friend=otherId)

        # If we didn't find one then try with https
        if len(follows) == 0:
            follows = Follow.objects.filter(author=author, friend=otherIdHttps)

        # Start data return
        data = {}
        data['query'] = 'friends'

        # If we didn't find something this time then they're definitely not
        # friends as far as we can tell
        if len(follows) == 0:
            data['authors'] = [author.id, otherId]
            data['friends'] = False
        else:
            follow = follows[0]
            data['authors'] = [author.id, follow.friend]
            data['friends'] = True

        return JSONResponse(data)
