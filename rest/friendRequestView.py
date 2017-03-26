from rest_framework.views import APIView

from dash.models import Author, FriendRequest
from .dataUtils import validateData, getFriendRequestData
from .verifyUtils import friendRequestValidators, NotFound, RequestExists
from .httpUtils import JSONResponse

class FriendRequestView(APIView):
    """
    This view gets authors.
    """
    def post(self, request):
        # Get data and validate it
        data = getFriendRequestData(request)
        validateData(data, friendRequestValidators)

        authorId = data['author']['id']
        requestorId = data['friend']['id']
        try:
            author = Author.objects.get(id=authorId)
        except Author.DoesNotExist:
            raise NotFound('author', authorId)

        fqs = FriendRequest.objects.filter(requestee=author,
                                           requester=requestorId)

        # Don't duplicate friend requests
        if len(fqs) > 0:
            raise RequestExists({'query': data['query'],
                                 'author.id': authorId,
                                 'friend.id': requestorId})

        fq = FriendRequest()
        fq.requestee = author
        fq.requester = requestorId
        fq.save()

        return JSONResponse({'success': True})
