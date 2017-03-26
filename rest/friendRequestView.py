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

        # Try to find the local author, 404 if you can't
        authorId = data['author']['id']
        requestorId = data['friend']['id']
        # save displayname of requestor to friendrequest table
        requestorName = data['friend']['displayName']
        try:
            author = Author.objects.get(id=authorId)
        except Author.DoesNotExist:
            raise NotFound('author', authorId)


        # Don't duplicate friend requests
        fqs = FriendRequest.objects.filter(requestee=author,
                                           requester=requestorId)
        if len(fqs) > 0:
            raise RequestExists({'query': data['query'],
                                 'author.id': authorId,
                                 'friend.id': requestorId})

        # Make new friend request
        fq = FriendRequest()
        fq.requestee = author
        fq.requester = requestorId
        fq.requesterDisplayName = requestorName
        fq.save()

        # Build return
        rv = {}
        rv['query'] = data['query']
        rv['author.id'] = authorId
        rv['friend.id'] = requestorId
        rv['success'] = True

        return JSONResponse(rv)
