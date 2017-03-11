from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.StreamView.as_view(), name='dash'),
    url(r'^newpost/$', views.newPost, name='newpost'),
    url(r'^newcomment/$', views.newComment, name='newcomment'),
    url(r'^friends/?$', views.friend_handler, name='friend_handler'),
    url(r'^friendrequest/?$', views.friendrequest_handler, name='friendrequest_handler'),
]
