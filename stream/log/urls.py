from django.conf.urls import url
from . import views
from .forms import LoginForm

urlpatterns = [
    url(r'^login/$', views.login, {'template_name': 'login.html', 'authentication_form': LoginForm}, name='login'),
    url(r'^logout/$', views.logout, {'next_page': '/login'}),
]
