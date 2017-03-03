# Author: Braedy Kuzma
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'posts/(?P<pid>[0-9a-fA-F\-]+)/$', views.post, name='post'),
]
