# Author: Braedy Kuzma

import uuid
import json
import re
from datetime import datetime

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
import django.utils.timezone as timezone
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView

from dash.models import Post, Comment, Author
from .serializers import PostSerializer
from .utils import InvalidField, NotFound, MalformedBody, MalformedId, \
                   ResourceConflict, MissingFields

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

def pidToUrl(request, pid):
    """
    Change a URL pid to a locally valid post id URL.

    Returns a url string on success or an appropriate HttpResponse on failure.
    """
    try:
        urlUuid = uuid.UUID(pid)
        url = 'http://' + request.get_host() + '/posts/' + urlUuid.hex + '/'
    except ValueError:
        # Include the bad ID in the response
        raise MalformedId('post', request.build_absolute_uri(request.path))

    return url

def getPost(request, pid):
    """
    Get a post by pid in URL.

    pid = Post id (uuid4, any valid format available from uuid python lib)

    Returns a post object on success or an appropriate HttpResponse on failure.
    """
    # Get url or error response
    url = pidToUrl(request, pid)
    try:
        post = Post.objects.get(id=url)
    # Url was valid but post didn't exist
    except Post.DoesNotExist:
        # Include the bad ID in the response
        raise NotFound('post', request.build_absolute_uri(request.path))

    return post

# Only compile this once because it's always the same and they're intensive
__imageContentTypeRE = re.compile(r'image/\w*\s*;\s*base64')
def getPostData(request, required):
    """
    Returns post data or error if data validation fails.
    """
    try:
        data = json.loads(str(request.body, encoding='utf-8'))
    except json.decoder.JSONDecodeError:
        return MalformedBody(request.body)

    # Make sure we have required fields
    notFound = []
    for key in required:
        if key not in data:
            notFound.append(key)

    # If we didn't find required keys return an error
    if notFound:
        raise MissingFields(notFound)

    # Normalize the contentType
    data['contentType'] = data['contentType'].strip()
    contentType = data['contentType']

    # Ensure we have a valid contentType
    # Is it a text type?
    if contentType not in ['text/plain', 'text/markdown']:

        # Not a text type, try the image RE match (intensive, so we only do this
        # if it's not text)
        # If this fails it's an invalid contentType
        match = __imageContentTypeRE.match(contentType)
        if not (match and match.span()[1] == len(contentType)):
            raise InvalidField('contentType', contentType)

    # Verify that author is a valid local id
    if not Author.objects.filter(id=data['author']).exists():
        raise InvalidField('author', data['author'])

    if data['visibility'] not in ['PUBLIC', 'FOAF', 'FRIENDS', 'PRIVATE', \
            'SERVERONLY']:
        raise InvalidField('visibility', data['visibility'])

    # Verify that if published exists it's a valid date
    if 'published' in data:
        date = parse_datetime(data['published'])
        if not date:
            raise InvalidField('published', data['published'])

    # Verify that if unlisted exists it's a valid bool
    if 'unlisted' in data and data['unlisted'] not in ['true', 'True', 'false', 'False']:
        raise InvalidField('unlisted', data['unlisted'])

    return data

class PostView(APIView):
    """
    REST view of an individual Post.
    """
    def delete(self, request, pid=None):
        # Get the post
        post = getPost(request, pid)

        # Save the id for the return
        postId = post.id

        # Delete the post
        post.delete()

        # Return
        data = {'deleted': postId}
        return JSONResponse(data)

    def get(self, request, pid=None):
        # Get post
        post = getPost(request, pid)

        # Serialize post
        postSer = PostSerializer(post)
        postData = postSer.data

        # TODO: Add query?
        # postData['query'] = 'post'

        return JSONResponse(postData)

    def post(self, request, pid=None):
        try:
            # This has the potential to raise NotFound AND MalformedId
            # If it's MalformedId we want it to fail
            post = getPost(request, pid)
        # We WANT it to be not found
        except NotFound:
            pass
        # No error was raised which means it already exists
        else:
            raise ResourceConflict('post',
                                   request.build_absolute_uri(request.path))

        # Get url or error response
        url = pidToUrl(request, pid)

        # Define required fields in post POST
        reqFields = ['author', 'title', 'content', 'contentType', 'visibility']

        # Get data, return error response if bad data
        data = getPostData(request, reqFields)

        # Fill in required fields
        post = Post()
        post.id = url
        post.title = data['title']
        post.contentType = data['contentType']
        post.content = data['content']
        post.author = Author.objects.get(id=data['author'])
        post.visibility = data['visibility']

        # Fill in unrequired fields
        post.unlisted = data.get('unlisted', False)
        post.description = data.get('description', '')
        post.published = data.get('published', timezone.now())

        # Save
        post.save()

        # Return
        data = {'created': post.id}
        return JSONResponse(data)
