# Author: Braedy Kuzma

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
import uuid
from dash.models import Post
from .serializers import PostSerializer

# Initially taken from
# http://www.django-rest-framework.org/tutorial/1-serialization/
class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

@csrf_exempt
def post(request, pid=None):
    """
    REST view of Post.

    pid = Post id (uuid4)
    """
    try:
        uuid.UUID(pid)
    except ValueError:
        return HttpResponse(status=500) # Bad uuid = malformed client request

    try:
        post = Post.objects.get(uuid=pid)
    except Post.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = PostSerializer(post)
        return JSONResponse(serializer.data)
    elif request.method == 'DELETE':
        post.delete()
        return HttpResponse(status=204)
