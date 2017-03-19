from django.http import HttpResponse
from rest_framework.views import exception_handler
from rest_framework.renderers import JSONRenderer

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
