from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from . import views


urlpatterns = [
    url(r'^$', views.StreamView.as_view(), name='dash'),
    url(r'^manager/$', views.ManagerView.as_view(), name='manager'),
    url(r'^newpost/$', views.newPost, name='newpost'),
    url(r'^editpost/$', views.editPost, name='editpost'),
    url(r'^newcomment/$', views.newComment, name='newcomment'),
    url(r'^friendrequest/$', views.friendRequest, name='friendrequest'),
    url(r'^posts/(?P<pid>[0-9a-fA-F\-]+)/$', views.post, name='post'),
    #url(r'^follow/$', views.FollowForm.as_view(), name='follow_form'),
    #url(r'^followrequests/$', views.FollowRequests, name='follow_requests'),
    #url(r'^following/$', views.ListFollowsAndFriends.as_view(), name='follow_form'),
]
