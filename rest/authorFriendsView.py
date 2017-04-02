from rest_framework.views import APIView

from dash.models import Follow
from .serializers import AuthorSerializer
from .dataUtils import validateData, getAuthor, getFriendsListData
from .verifyUtils import multiFriendQueryValidators, DependencyError
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

    def post(self, request, aid):
        """
        Rather than posting a list of friends to add this is a question about
        whether or not a list of author id urls are friends with the POST'd to
        user.
        """
        # Get the author requested
        author = getAuthor(request, aid)

        # Get the data from the POST
        data = getFriendsListData(request)
        validateData(data, multiFriendQueryValidators)

        # Ensure that they POST'd to the url they said they were POSTing to
        if author.id != data['author']:
            data = {'author.id': author.id,
                    'query.author': data['author']}
            raise DependencyError(data)

        # Get all follows for the author ONCE. Filter later.
        authorFollows = Follow.objects.filter(author=author)

        # This is the list of people we consider friends from the list they sent
        ourFriends = []

        for friendId in data['authors']:
            try:
                # We don't actually care what we get back, if it doesn't throw
                # an exception then we're friends
                authorFollows.get(friend=friendId)
                ourFriends.append(friendId)
            except Follow.DoesNotExist:
                # If there's an exception we don't care, just move on
                pass

        # Our return data
        rv = {
            'query': 'friends',
            'author': author.id,
            'friends': ourFriends
        }

        return JSONResponse(rv)

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
