import re

from django.http import HttpResponse
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from rest_framework.views import exception_handler
from rest_framework.renderers import JSONRenderer

from dash.models import Author

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
        self.status=status

class MalformedId(DefaultException):
    """
    Exception for an invalid request id. This is NOT a not found, this exception
    indicates the id wasn't in a valid form so we couldn't even look for the
    resource.
    """
    def __init__(self, objectName, objectId):
        DefaultException.__init__(self, {objectName + '_id': objectId}, 400)

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

class NotFound(DefaultException):
    """
    Exception for a request that was looking for a resource that couldn't be
    found.
    """
    def __init__(self, objectName, objectId):
        DefaultException.__init__(self, {objectName + '_id': objectId}, 404)

class ResourceConflict(DefaultException):
    """
    Exception for a request trying to create a resource where one already
    exists.
    """
    def __init__(self, objectName, objectId):
        DefaultException.__init__(self, {objectName + '_id': objectId}, 409)

class MissingFields(DefaultException):
    """
    Exception for a request trying to create a resource while missing required
    fields.
    """
    def __init__(self, fields):
        DefaultException.__init__(self, {'required': fields}, 422)

class MalformedBody(DefaultException):
    """
    Exception for a request with malformed json body.
    """
    def __init__(self, body):
        DefaultException.__init__(self, {'json': body}, 400)

def exceptionHandler(exc, context):
    if isinstance(exc, DefaultException):
        response = JSONResponse(exc.data, status=exc.status)
    else:
        response = exception_handler(exc, context)

    return response

#################
# Data validation
#################

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
        print(e)
        raise InvalidField(name, value)
    return value

def validateURLList(data, name, value):
    """
    Validate that a value is a list and that it contains URLs.
    """
    validateList(name, value)
    for i, url in enumerate(value):
        try:
            value[i] = validateURL({}, '', url)
        # Catch the InvalideField for the URL and raise our own for the list
        except InvalidField:
            raise InvalidField(name, value)
    return value

def validateVisibleTo(data, name, value):
    visibility = data['visibility']
    if visibility != 'PRIVATE':
        raise DependencyError({'visibility': visibility, name: value})

    # No need to catch and override any errors from this
    validateURLList(data, name, value)

# Fields we can validate on incoming data for posts
postValidators = (
    ('title', lambda d, k, v: v), # Title requires no validation
    ('description', lambda d, k, v: v), # Description requires no validation
    ('contentType', validateContentType),
    ('content', lambda d, k, v: v), # Content requires no validation
    ('author', validateAuthorExists),
    ('published', validateDate),
    ('visibility', validateVisibility),
    ('unlisted', validateBool),
    ('categories', validateList),
    ('visibleTo', validateVisibleTo)
)
