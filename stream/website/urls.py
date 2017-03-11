#!python
# log/urls.py
from django.conf.urls import url
from . import views
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
#from .views import register

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^register_success/$', views.register_success, name='register_success'),
    url(r'^requests/$', views.friend_requests, name='requests'),
    url(r'^friends/$', views.friends, name='friends'),
]
