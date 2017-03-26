import re
import uuid
import functools

from django.http import HttpResponse
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_datetime
from rest_framework.views import exception_handler
from rest_framework.renderers import JSONRenderer

from dash.models import Author
from .httpUtils import JSONResponse

#####################
#  Exception handling
#####################

class DefaultException(Exception):
    """
    Default exception because rest_framework's default API exception wouldn't
    allow me to manage response data directly like I wanted to.
    """
    def __init__(self, data, status):
        self.data = data
        self.status = status

class MalformedId(DefaultException):
    """
    Exception for an invalid request id. This is NOT a not found, this exception
    indicates the id wasn't in a valid form so we couldn't even look for the
    resource.
    """
    def __init__(self, objectName, objectId):
        DefaultException.__init__(self, {objectName + '.id': objectId}, 400)

class MalformedBody(DefaultException):
    """
    Exception for a request with malformed json body.
    """
    def __init__(self, body):
        DefaultException.__init__(self, {'json': body}, 400)

class InvalidField(DefaultException):
    """
    Exception for a missing field.
    """
    def __init__(self, name, value):
        DefaultException.__init__(self, {name: value}, 400)

class DependencyError(DefaultException):
    """
    Exception for a field with a dependency on another failing.
    """
    def __init__(self, values):
        DefaultException.__init__(self, values, 400)

class QueryError(InvalidField):
    """
    Exception for a query that isn't accepted by an endpoint.
    """
    def __init__(self, query):
        InvalidField.__init__(self, 'query', query)

class NotVisible(DefaultException):
    """
    Excception for when something shouldn't be visible to the outside
    so we're denying access.
    """
    def __init__(self, reason):
        DefaultException.__init__(self, {'reason': reason}, 403)

class NotFound(DefaultException):
    """
    Exception for a request that was looking for a resource that couldn't be
    found.
    """
    def __init__(self, objectName, objectId):
        DefaultException.__init__(self, {objectName + '.id': objectId}, 404)

class ResourceConflict(DefaultException):
    """
    Exception for a request trying to create a resource where one already
    exists.
    """
    def __init__(self, objectName, objectId):
        DefaultException.__init__(self, {objectName + '.id': objectId}, 409)

class RequestExists(DefaultException):
    """
    Exception for when an (id-less) request already exists and there was no need
    to re-request it.
    e.g. a friend request
    """
    def __init__(self, requestParams):
        DefaultException.__init__(self, requestParams, 409)

class MissingFields(DefaultException):
    """
    Exception for a request trying to create a resource while missing required
    fields.
    """
    def __init__(self, fields):
        DefaultException.__init__(self, {'required': fields}, 422)

def exceptionHandler(exc, context):
    if isinstance(exc, DefaultException):
        response = JSONResponse(exc.data, status=exc.status)
    else:
        response = exception_handler(exc, context)

    return response

#################
# Data validation
#################

def validateNothing(data, name, value):
    return value

# Only compile this once because it's always the same and they're intensive
__imageContentTypeRE = re.compile(r'image/\w*\s*;\s*base64')
def validateContentType(data, name, contentType):
    """
    Clean up contentType and ensure it's one of text/plain, text/markdown,
    image/*;base64.
    """
    # Normalize the contentType
    contentType = contentType.strip()

    # Ensure we have a valid contentType
    # Is it a text type?
    if contentType not in ['text/plain', 'text/markdown']:
        # Not a text type, try the image RE match (intensive, so we only do this
        # if it's not text)
        # If this fails it's an invalid contentType
        match = __imageContentTypeRE.match(contentType)
        if not (match and match.span()[1] == len(contentType)):
            raise InvalidField(name, contentType)

    return contentType

def validateAuthorExists(data, name, authorId):
    """
    Verify that the author id exists in our database.
    """
    # Verify that author is a valid local id
    if not Author.objects.filter(id=authorId).exists():
        raise InvalidField(name, authorId)
    return authorId

def validateVisibility(data, name, visibility):
    """
    Verify that visibility is one of PUBLIC, FOAF, FRIENDS, PRIVATE, SERVERONLY.
    """
    # Check visibility/visibileTo mismatch
    if visibility != 'PRIVATE':
        # If visibileTo is being set and it's not emtpy, it's an error
        if 'visibleTo' in data and data['visibleTo']:
            raise DependencyError({'visibleTo': data['visibleTo'],
                                   name: visibility})
        # Else if it's not in the data we can set it to the empty list. This
        # forces the data to be updated or set.
        # Note that if the key is in the data then it must already be empty
        # Also note that we don't care about the order of validation between
        # visibileTo and visibility after this change because we know []
        # is a valid value
        elif 'visibleTo' not in data:
            data['visibleTo'] = []
    if visibility not in ['PUBLIC', 'FOAF', 'FRIENDS', 'PRIVATE', 'SERVERONLY']:
        raise InvalidField(name, visibility)
    return visibility

def validateDate(data, name, published):
    """
    Verify that a date string is valid.
    """
    # Verify that if published exists it's a valid date
    date = parse_datetime(published)
    if not date:
        raise InvalidField(name, published)
    return published

def validateBool(data, name, value):
    """
    Verify that a string could be translated to a valid bool.
    """
    value = value.capitalize()
    if value not in ['True', 'False']:
        raise InvalidField(name, value)
    return value

def validateList(data, name, value):
    """
    Verify that the value is a list.
    """
    if type(value) != list:
        raise InvalidField(name, value)
    return value

def validateURL(data, name, value):
    """
    Verify that a string is a URL.
    """
    validator = URLValidator()
    try:
        validator(value)
    except ValidationError as e:
        raise InvalidField(name, value)
    return value

def validateURLList(data, name, value):
    """
    Validate that a value is a list and that it contains URLs.
    """
    validateList(data, name, value)
    for i, url in enumerate(value):
        try:
            value[i] = validateURL({}, '', url)
        # Catch the InvalideField for the URL and raise our own for the list
        except InvalidField:
            raise InvalidField(name, value)
    return value

def validateVisibleTo(data, name, visibleTo):
    """
    Validate a field is a list of valid visibleTo URLs.
    """
    # If this isn't here then we're sure that visibility should still be PRIVATE
    # If it is here and it isn't empty then we need to raise an error
    if 'visibility' in data and visibleTo:
        visibility = data['visibility']
        if visibility != 'PRIVATE':
            raise DependencyError({'visibility': visibility, name: visibleTo, 'butts': 'hi'})

    # No need to catch and override any errors from this
    return validateURLList(data, name, visibleTo)

def validateUUID(data, name, uid):
    """
    Validate the field is a valid UUID.
    """
    try:
        urlUuid = uuid.UUID(uid)
    except ValueError:
        raise InvalidField(name, uid)
    return uid

def validateQuery(required, data, name, query):
    """
    Validate a field has a valid query. Should be used with functools.partial
    to specify the desired query.
    """
    if required != query:
        raise QueryError(query)
    return query


# Fields we can validate on incoming data for posts
postValidators = (
    ('title', validateNothing),
    ('description', validateNothing),
    ('contentType', validateContentType),
    ('content', validateNothing),
    ('author', validateAuthorExists),
    ('published', validateDate),
    ('visibility', validateVisibility),
    ('unlisted', validateBool),
    ('categories', validateList),
    ('visibleTo', validateVisibleTo)
)

authorValidators = (
    ('id', validateURL),
    ('host', validateURL),
    ('displayName', validateNothing),
    ('url', validateURL),
    ('github', validateURL)
)

commentValidators = (
    ('comment', validateNothing),
    ('contentType', validateContentType),
    ('published', validateDate),
    ('id', validateUUID),
    ('author', authorValidators)
)

addCommentValidators = (
    ('id', validateUUID),
    ('query', functools.partial(validateQuery, 'addComment')),
    ('post', validateURL),
    ('comment', commentValidators)
)

friendRequestValidators = (
    ('query', functools.partial(validateQuery, 'friendrequest')),
    ('author', authorValidators),
    ('friend', authorValidators)
)
