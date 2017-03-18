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

from dash.models import Post, Comment, Author
from .serializers import PostSerializer

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
        errorData = {'post_id': request.build_absolute_uri(request.path)}
        return JSONResponse(errorData, status=400) # Bad uuid = malformed client request

    return url

def getPost(request, pid):
    """
    Get a post by pid in URL.

    pid = Post id (uuid4, any valid format available from uuid python lib)

    Returns a post object on success or an appropriate HttpResponse on failure.
    """
    # Get url or error response
    url = pidToUrl(request, pid)
    if isinstance(url, HttpResponse):
        return url

    try:
        post = Post.objects.get(id=url)

    # Url was valid but post didn't exist
    except Post.DoesNotExist:
        # Include the bad ID in the response
        errorData = {'post_id': request.build_absolute_uri(request.path)}
        return JSONResponse(errorData, status=404)

     # Some how the id matched multiple posts
    except Post.MultipleObjectsReturned:
        # Include the bad ID in the response
        errorData = {'post_id': request.build_absolute_uri(request.path)}
        return JSONResponse(errorData, status=500)

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
        errorData = {'malformed_json': True}
        return JSONResponse(errorData, status=400)

    # Make sure we have required fields
    notFound = []
    for key in required:
        if key not in data:
            notFound.append(key)

    # If we didn't find required keys return an error
    if notFound:
        errorData = {'required': notFound}
        return JSONResponse(errorData, status=422)

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
            errorData = {'contentType': contentType}
            return JSONResponse(errorData, status=400)

    # Verify that author is a valid local id
    if not Author.objects.filter(id=data['author']).exists():
        errorData = {'author': data['author']}
        return JSONResponse(errorData, status=400)

    if data['visibility'] not in ['PUBLIC', 'FOAF', 'FRIENDS', 'PRIVATE', \
            'SERVERONLY']:
        errorData = {'visibility': data['visibility']}
        return JSONResponse(errorData, status=400)

    # Verify that if published exists it's a valid date
    if 'published' in data:
        date = parse_datetime(data['published'])
        if not date:
            errorData = {'published': data['published']}
            return JSONResponse(errorData, status=400)

    # Verify that if unlisted exists it's a valid bool
    if 'unlisted' in data and data['unlisted'] not in ['true', 'True', 'false', 'False']:
        errorData = {'unlisted': data['unlisted']}
        return JSONResponse(errorData, status=400)

    return data

@csrf_exempt
def post(request, pid=None):
    """
    REST view of Post.

    pid = Post id (uuid4, any valid format available from uuid python lib)
    """
    if request.method in ['GET', 'DELETE']:
        # Get post or error response
        post = getPost(request, pid)
        if isinstance(post, HttpResponse):
            return post

        if request.method == 'GET':
            postSer = PostSerializer(post)
            postData = postSer.data

            # TODO: Add query?
            # postData['query'] = 'post'

            return JSONResponse(postData)
        elif request.method == 'DELETE':
            post.delete()
            return HttpResponse(status=204)
    elif request.method == 'POST':
        post = getPost(request, pid)
        if isinstance(post, Post):
            data = {'post_id': request.build_absolute_uri(request.path)}

            # Return 409 Conflict if an instance exists at this id
            return JSONResponse(data, status=409)

        # Get url or error response
        url = pidToUrl(request, pid)
        if isinstance(url, HttpResponse):
            return url

        # Define required fields in post POST
        reqFields = ['author', 'title', 'content', 'contentType', 'visibility']

        # Get data, return error response if bad data
        data = getPostData(request, reqFields)
        if isinstance(data, HttpResponse):
            return data

        post = Post()

        # Fill in required fields
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

        post.save()

        # Fill in unrequired fields

        return HttpResponse(status=204)
