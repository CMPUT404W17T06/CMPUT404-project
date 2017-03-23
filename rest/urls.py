# Author: Braedy Kuzma
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^posts/(?P<pid>[0-9a-fA-F\-]+)/$', views.PostView.as_view(),
        name='post'),
    url(r'^posts/$', views.PostsView.as_view(), name='posts'),
    url(r'^author/(?P<aid>[0-9a-fA-F\-]+)/$', views.AuthorView.as_view(),
        name='author')
]
