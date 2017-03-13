from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from . import views


urlpatterns = [
    url(r'^$', views.StreamView.as_view(), name='dash'),
    url(r'^manager/$', views.ManagerView.as_view(), name='manager'),
    url(r'^newpost/$', views.newPost, name='newpost'),
    url(r'^editpost/$', views.editPost, name='editpost'),
    url(r'^newcomment/$', views.newComment, name='newcomment'),
    url(r'^posts/(?P<pid>[0-9a-fA-F\-]+)/$', views.post, name='post'),
    url(r'^friends/(?P<author1_id>[0-9a-z-]+)/(?P<author2_id>[0-9a-z-]+)/?$', views.friend_query_handler, name='friend_query_handler'),
    url(r'^friends/(?P<id>[^/]+)/?$', views.friend_handler_specific, name='friend_handler_specific'),
    url(r'^friends/?$', views.friend_handler, name='friend_handler'),
    url(r'^friendrequest/?$', views.friendrequest_handler, name='friendrequest_handler'),
]
