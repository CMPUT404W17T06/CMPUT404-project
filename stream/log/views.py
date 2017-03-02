# this is actually importing views here, we might need to override these in the future
from django.contrib.auth.views import login, logout

# Create your views here.
# this login required decorator is to not allow to any
# view without authenticating
