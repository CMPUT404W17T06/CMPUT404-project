# Author Braedy Kuzma

from django.core.paginator import Paginator, InvalidPage
from rest_framework.views import APIView

from dash.models import Post
from .serializers import PostSerializer
from .dataUtils import getAuthor
from .httpUtils import JSONResponse

class AuthorPostView(APIView):
    """
    This is for viewing all of the posts that a single author has made.
    """
    def get(self, request, aid):
        # Try to pull page number out of GET
        try:
            pageNum = int(request.GET.get('page', 0))
        except ValueError:
            raise InvalidField('page', request.GET.get('page'))

        # Paginator one-indexes for some reason...
        pageNum += 1

        # Try to pull size out of GET
        try:
            size = int(request.GET.get('size', 50))
        except ValueError:
            raise InvalidField('size', request.GET.get('size'))

        # Only serve max 100 posts per page
        if size > 100:
            size = 100

        # Get the author
        author = getAuthor(request, aid)

        # Get their posts and exclude server only and unlisted
        posts = Post.objects.filter(author=author) \
                            .exclude(unlisted=True) \
                            .exclude(visibility="SERVERONLY")
        count = posts.count()

        # Set up the Paginator
        pager = Paginator(posts, size)

        # Get our page
        try:
            page = pager.page(pageNum)
        except InvalidPage:
            data = {'query': 'posts',
                    'count': count,
                    'posts': [],
                    'size': 0}

            if pageNum > pager.num_pages:
                # Last page is num_pages - 1 because zero indexed for external
                uri = request.build_absolute_uri('?size={}&page={}'\
                                                 .format(size,
                                                         pager.num_pages - 1))
                data['last'] = uri
            elif pageNum < 1:
                # First page is 0 because zero indexed for external
                uri = request.build_absolute_uri('?size={}&page={}'\
                                                 .format(size, 0))
                data['first'] = uri
            else:
                # Just reraise the error..
                raise

            return JSONResponse(data)


        # Start our query response
        respData = {}
        respData['query'] = 'posts'
        respData['count'] = count
        respData['size'] = size if size < len(page) else len(page)

        # Now get our data
        postSer = PostSerializer(page, many=True)
        respData['posts'] = postSer.data

        # Build and our next/previous uris
        # Next if one-indexed pageNum isn't already the page count
        if pageNum != pager.num_pages:
            # Just use page num, we've already incremented and the external
            # inteface is zero indexed
            uri = request.build_absolute_uri('?size={}&page={}'\
                                             .format(size, pageNum))
            respData['next'] = uri

        # Previous if one-indexed pageNum isn't the first page
        if pageNum != 1:
            # Use pageNum - 2 because we're using one indexed pageNum and the
            # external interface is zero indexed
            uri = request.build_absolute_uri('?size={}&page={}'\
                                             .format(size, pageNum - 2))
            respData['previous'] = uri

        return JSONResponse(respData)
