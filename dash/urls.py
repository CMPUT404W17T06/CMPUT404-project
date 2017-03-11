from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.StreamView.as_view(), name='dash'),
    url(r'^newpost/$', views.newPost, name='newpost'),
    url(r'^newcomment/$', views.newComment, name='newcomment'),
]
