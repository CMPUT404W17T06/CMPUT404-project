# Author: Braedy Kuzma
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^posts/$', views.PostsView.as_view(), name='posts'),
    url(r'^posts/(?P<pid>[0-9a-fA-F\-]+)/$', views.PostView.as_view(),
        name='post'),
    url(r'^posts/(?P<pid>[0-9a-fA-F\-]+)/comments/$',
        views.CommentView.as_view(), name='comments'),
    url(r'^author/posts/$', views.PostsView.as_view(), name='authorpost'),
    url(r'^author/(?P<aid>[0-9a-fA-F\-]+)/$', views.AuthorView.as_view(),
        name='author'),
    url(r'^author/(?P<aid>[0-9a-fA-F\-]+)/friends/$',
        views.AuthorFriendsView.as_view(), name='friends'),
    url(r'^friendrequest/$', views.FriendRequestView.as_view(),
        name='friendrequest'),
    url(r'^author/(?P<aid>[0-9a-fA-F\-]+)/friends/'
        r'(?P<other>[\w\-\.]+(:\d{2,5})?(/[0-9a-fA-F\-]+)*/)$',
        views.AuthorIsFriendsView.as_view(), name='isfriends')
]
