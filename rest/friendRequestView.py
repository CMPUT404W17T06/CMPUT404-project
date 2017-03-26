from rest_framework.views import APIView

from dash.models import Author, FriendRequest
from .dataUtils import validateData, getFriendRequestData
from .verifyUtils import friendRequestValidators, NotFound
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
        try:
            author = Author.objects.get(id=authorId)
        except Author.DoesNotExist:
            raise NotFound('author', authorId)

        fq = FriendRequest()
        fq.requestee = author
        fq.requester = data['friend']['id']
        fq.save()

        return JSONResponse({'success': True})
