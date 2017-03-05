from django.conf.urls import url
from . import views
from .forms import LoginForm
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm

urlpatterns = [
    url(r'^login/$', views.login, {'template_name': 'login.html', 'authentication_form': LoginForm}, name='login'),
    url(r'^logout/$', views.logout, {'next_page': '/login'}),
    url(r'^register_success/$', views.register_success, name='register_success'),
    url(r'^register/$', views.UserRegisterForm.as_view(), name='register'),
    url(r'^login/register/$', views.UserRegisterForm.as_view(), name='register'),
 
]
