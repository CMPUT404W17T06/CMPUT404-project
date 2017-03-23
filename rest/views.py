# Author: Braedy Kuzma

import uuid
import json
from datetime import datetime

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
import django.utils.timezone as timezone
from django.core.paginator import Paginator, InvalidPage
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView

from dash.models import Post, Comment, Author, Category, CanSee
from .serializers import PostSerializer, AuthorSerializer, CommentSerializer
from .utils import InvalidField, NotFound, MalformedBody, MalformedId, \
                   ResourceConflict, MissingFields
from .utils import postValidators

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

def validateData(data, fields):
    """
    Validates data in a dictionary using validation functions.

    Validation functions should take 3 arguments, the full data (for dependency
    validation), the data name, and the data.
    Validation functions return a updated, validated version of their value.
    Validation functions should raise InvalidField exceptions when they fail to
    validate their data or DependencyError if a precondition fails.
    """
    for key, validator in fields:
        if key in data:
            data[key] = validator(data, key, data[key])

def requireFields(data, required):
    """
    Ensure that data has required fields. No return on success.

    Raises MissingFields if fields are missing from data.
    """
    # Make sure we have required fields
    notFound = []
    for key in required:
        if key not in data:
            notFound.append(key)

    # If we didn't find required keys return an error
    if notFound:
        raise MissingFields(notFound)

def pidToUrl(request, pid):
    """
    Change a URL pid to a locally valid post id URL.

    Returns a url string on success or raises MalformedId.
    """
    try:
        urlUuid = uuid.UUID(pid)
        url = 'http://' + request.get_host() + '/posts/' + urlUuid.hex + '/'
    except ValueError:
        # Include the bad ID in the response
        raise MalformedId('post', request.build_absolute_uri(request.path))

    return url

def aidToUrl(request, pid):
    """
    Change a url aid to a locally valid author id URL.

    Returns a url string on success or raises MalformedId.
    """
    try:
        urlUuid = uuid.UUID(pid)
        url = 'http://' + request.get_host() + '/author/' + urlUuid.hex + '/'
    except ValueError:
        # Include the bad ID in the response
        raise MalformedId('author', request.build_absolute_uri(request.path))

    return url

def getPost(request, pid):
    """
    Get a post by pid in URL.

    pid = Post id (uuid4, any valid format available from uuid python lib)

    Returns a post object on success, raises NotFound on failure.
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

def getAuthor(request, aid):
    """
    Get an author by aid in URL.

    aid = Author id (uuid4, any valid format available from uuid python lib)

    Returns an Author object on success, raises NotFound on failure.
    """
    # Get url or error response
    url = aidToUrl(request, aid)
    try:
        author = Author.objects.get(id=url)
    # Url was valid but author didn't exist
    except Author.DoesNotExist:
        # Include the bad ID in the response
        raise NotFound('author', request.build_absolute_uri(request.path))

    return author

def getPostData(request, require=True):
    """
    Returns post data from POST request.
    Raises MalformedBody if post body was malformed.
    """
    # Ensure that the body of the request is valid
    try:
        data = json.loads(str(request.body, encoding='utf-8'))
    except json.decoder.JSONDecodeError:
        raise MalformedBody(request.body)

    # Ensure required fields are present
    if require:
        required = ('author', 'title', 'content', 'contentType', 'visibility')
        requireFields(data, required)

    return data

class PostView(APIView):
    """
    REST view of an individual Post.
    """
    def delete(self, request, pid=None):
        """
        Deletes a post.
        """
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
        """
        Gets a post.
        """
        # Get post
        post = getPost(request, pid)

        # Serialize post
        postSer = PostSerializer(post)
        postData = postSer.data

        # TODO: Add query?
        # postData['query'] = 'post'

        return JSONResponse(postData)

    def post(self, request, pid=None):
        """
        Creates a post.
        """
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

        # Get and validate data
        data = getPostData(request)
        validateData(data, postValidators)

        # Get id url
        url = pidToUrl(request, pid)

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

        # Were there any categories?
        if 'categories' in data and data['categories']:
            categoryList = data['categories']

            # Build Category objects
            for categoryStr in categoryList:
                category = Category()
                category.category = categoryStr
                category.post = post
                category.save()

        # Were there any users this should be particularly visibleTo
        if 'visibleTo' in data and data['visibleTo']:
            visibleToList = data['visibleTo']

            # Build can see list
            for authorId in visibleToList:
                canSee = CanSee()
                canSee.post = post
                canSee.visibleTo = authorId
                canSee.save()

        # Return
        data = {'created': post.id}
        return JSONResponse(data)

    def put(self, request, pid=None):
        """
        Updates a post.
        """
        # Get post
        post = getPost(request, pid)

        # Get data from PUT, don't require any fields
        data = getPostData(request, require=False)
        validateData(data, postValidators)

        # Update fields as appropriate
        post.title = data.get('title', post.title)
        post.description = data.get('description', post.description)
        post.published = data.get('published', post.published)
        post.contentType = data.get('contentType', post.contentType)
        post.content = data.get('content', post.content)
        post.author = Author.objects.get(id=data['author']) \
                      if 'author' in data else \
                      post.author
        post.visibility = data.get('visibility', post.visibility)
        post.unlisted = data.get('unlisted', post.unlisted)

        post.save()

        # Should we update categories?
        if 'categories' in data:
            # Destroy the old categories
            oldCategories = Category.objects.filter(post=post)
            for category in oldCategories:
                category.delete()

            # Build new categories
            categoryList = data['categories']

            # Build Category objects
            for categoryStr in categoryList:
                category = Category()
                category.category = categoryStr
                category.post = post
                category.save()

        # Should we update the visibleTos?
        if 'visibleTo' in data:
            # Destroy old can sees
            oldCanSees = CanSee.objects.filter(post=post)
            for canSee in oldCanSees:
                canSee.delete()

            # Build new can sees
            visibleToList = data['visibleTo']

            # Build can see list
            for authorId in visibleToList:
                canSee = CanSee()
                canSee.post = post
                canSee.visibleTo = authorId
                canSee.save()

        # Return
        data = {'updated': post.id}
        return JSONResponse(data)

class PostsView(APIView):
    """
    This is the get multiple posts view and uses Pagination to display posts.
    """
    def get(self, request):
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

        # Get posts and the count
        posts = Post.objects.exclude(visibility='SERVERONLY')
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

        return JSONResponse(respData, status=200)

class AuthorView(APIView):
    """
    This view gets authors.
    """
    def get(self, request, aid):
        # Get author
        author = getAuthor(request, aid)
        authSer =  AuthorSerializer(author)
        return JSONResponse(authSer.data)

class CommentView(APIView):
    """
    This view gets
    """
    def get(self, request, pid):
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

        # Only serve max 100 comments per page
        if size > 100:
            size = 100

        # Get comments and the count
        post = getPost(request, pid)
        comments = Comment.objects.filter(post=post)
        count = comments.count()

        # Set up the Paginator
        pager = Paginator(comments, size)

        # Get our page
        try:
            page = pager.page(pageNum)
        except InvalidPage:
            data = {'query': 'comments',
                    'count': count,
                    'comments': [],
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
        respData['query'] = 'comments'
        respData['count'] = count
        respData['size'] = size if size < len(page) else len(page)

        # Now get our data
        comSer = CommentSerializer(page, many=True)
        respData['comments'] = comSer.data

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

        return JSONResponse(respData, status=200)
