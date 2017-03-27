from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from . import views


urlpatterns = [
    url(r'^$', views.StreamView.as_view(), name='dash'),
    url(r'^manager/$', views.ManagerView.as_view(), name='manager'),
    url(r'^newpost/$', views.newPost, name='newpost'),
    url(r'^newcomment/$', views.newComment, name='newcomment'),
    url(r'^friendrequest/$', views.SendFriendRequest, name='friendrequest'),
    url(r'^posts/(?P<pid>[0-9a-fA-F\-]+)/$', views.post, name='post'),
    #url(r'^follow/$', views.FollowForm.as_view(), name='follow_form'),
    url(r'^following/$', views.ListFollowsAndFriends.as_view(), name='follow_form'),
]
