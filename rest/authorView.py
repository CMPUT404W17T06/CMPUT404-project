# Author: Braedy Kuzma

from rest_framework.views import APIView

from .serializers import AuthorSerializer
from .dataUtils import getAuthor
from .httpUtils import JSONResponse

class AuthorView(APIView):
    """
    This view gets authors.
    """
    def get(self, request, aid):
        # Get author
        author = getAuthor(request, aid)
        authSer =  AuthorSerializer(author)
        return JSONResponse(authSer.data)
