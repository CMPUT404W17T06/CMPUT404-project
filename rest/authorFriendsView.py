from rest_framework.views import APIView

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
