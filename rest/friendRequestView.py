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
        # This may seem backwards, but the friend field is supposed to be our
        # local author (the local author that the remote author wants to be
        # friends with). The author field is the requestor
        authorId = data['friend']['id']
        requestorId = data['author']['id']
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
        fq.save()

        # Build return
        # TODO update incoming code from friends branch
        rv = {}
        rv['query'] = data['query']
        rv['author.id'] = authorId
        rv['friend.id'] = requestorId
        rv['success'] = True

        return JSONResponse(rv)
