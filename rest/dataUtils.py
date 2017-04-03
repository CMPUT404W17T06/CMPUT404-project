# Author: Braedy Kuzma
import uuid
import json

from dash.models import Post, Author
from .verifyUtils import InvalidField, MissingFields, MalformedId, NotFound, \
                         MalformedBody

def validateData(data, fields):
    """
    Validates data in a dictionary using validation functions.

    Validation functions should take 3 arguments, the full data (for dependency
    validation), the data name, and the data.
    Validation functions return an updated, validated version of their value.
    Validation functions should raise InvalidField exceptions when they fail to
    validate their data or DependencyError if a precondition fails.
    """
    for key, validator in fields:
        if isinstance(validator, tuple):
            if key in data:
                try:
                    validateData(data[key], validator)
                except InvalidField as e:
                    for innerKey in e.data:
                        raise InvalidField(key + '.' + innerKey,
                                           e.data[innerKey])
            else:
                raise InvalidField(key, data[key])
        elif key in data:
            data[key] = validator(data, key, data[key])

def requireFields(data, required):
    """
    Ensure that data has required fields. No return on success.

    Raises MissingFields if fields are missing from data.
    """
    # Make sure we have required fields
    notFound = []
    for key in required:
        # If it's a tuple we need to recurse
        if isinstance(key, tuple):
            # The key wasn't even sent in the data
            if key[0] not in data:
                notFound.append(key[0])
            # If the data at the key isn't a dict then it's the wrong type
            # Say we're missing it and leave early
            elif not isinstance(data[key[0]], dict):
                notFound.append(key[0])
            # If the key is in the data recurse
            elif key[0] in data:
                # Recurse. Catch missing fields from below and append their
                # keys to make the output more useful
                try:
                    requireFields(data[key[0]], key[1])
                except MissingFields as e:
                    for missing in e.data['required']:
                        notFound.append(key[0] + '.' + missing)
            # It was a flat key and just wasn't found
            else:
                notFound.append(key[0])
        # It's not a tuple so it should be a key in this data, append to
        # notFound
        elif key not in data:
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
        badPath = '/posts/' + pid + '/'
        raise MalformedId('post', request.build_absolute_uri(badPath))

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
        badPath = '/posts/' + pid + '/'
        raise NotFound('post', request.build_absolute_uri(badPath))

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


def getData(request):
    """
    This tries to return valid JSON data from a request.
    Raises MalformedBody if POST body wasn't valid JSON.
    """
    try:
        return json.loads(str(request.body, encoding='utf-8'))
    except json.decoder.JSONDecodeError:
        raise MalformedBody(request.body)

def getPostData(request):
    """
    Returns post data from POST request.
    """
    data = getData(request)

    # Ensure required fields are present
    required = ('author', 'title', 'content', 'contentType', 'visibility')
    requireFields(data, required)

    return data

def getCommentData(request):
    """
    Returns comment data from POST request.
    """
    data = getData(request)

    # Ensure required fields are present
    required = (
        'query',
        'post',
        ('comment', (
            ('author', (
                'id',
                'host',
                'displayName'
            )),
            'comment',
            'contentType',
            'published',
            'id'
        ))
    )
    requireFields(data, required)

    return data

def getFriendRequestData(request):
    """
    Returns friend request data from POST request.
    """
    data = getData(request)

    authorRequired = ('id', 'host', 'displayName')
    required = (
        'query',
        ('author', authorRequired),
        ('friend', authorRequired)
    )
    requireFields(data, required)

    return data

def getFriendsListData(request):
    """
    Returns data about a multiple friend query.
    """
    data = getData(request)

    required = (
        'query',
        'author',
        'authors'
    )
    requireFields(data, required)

    return data
