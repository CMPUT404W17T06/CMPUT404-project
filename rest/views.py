# Author: Braedy Kuzma

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
import uuid
from dash.models import Post, Comment
from .serializers import PostSerializer, CommentSerializer

# Initially taken from
# http://www.django-rest-framework.org/tutorial/1-serialization/
class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json; charset=utf-8'
        super(JSONResponse, self).__init__(content, **kwargs)

@csrf_exempt
def post(request, pid=None):
    """
    REST view of Post.

    pid = Post id (uuid4)
    """
    try:
        urlUuid = uuid.UUID(pid)
    except ValueError:
        return HttpResponse(status=500) # Bad uuid = malformed client request

    try:
        url = 'http://' + request.get_host() + '/posts/' + urlUuid.hex
        post = Post.objects.get(id=url)
    except Post.DoesNotExist:
        return HttpResponse(status=404)
    except Post.MultipleObjectsReturned:
        return HttpResponse(status=500) # Some how the UUID matched multiple
                                        # posts

    if request.method == 'GET':
        postSer = PostSerializer(post)
        postData = postSer.data

        comments = Comment.objects.filter(post=post)
        commSer = CommentSerializer(comments, many=True)
        postData['comments'] = commSer.data
        return JSONResponse(postData)
    elif request.method == 'DELETE':
        post.delete()
        return HttpResponse(status=204)
