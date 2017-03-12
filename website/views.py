from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.generic import View
from django.db import transaction

from dash.models import Author
from rest.models import RemoteNode
from .forms import ProfileForm
from .forms import UserRegisterForm

import requests
import json
from requests.auth import HTTPBasicAuth
import uuid


# Create your views here.


@login_required(login_url="login/")
def home(request):
	return render(request, "home.html")


def register_success(request):
	return render(request, "register_success.html")


@login_required(login_url="login/")
def friend_requests(request):
	if (request.method == 'GET'):
		return render(request, 'requests.html')
	return HttpResponse(status=405)


@login_required(login_url="login/")
def friends(request):
	if (request.method == 'GET'):
		return render(request, 'friends.html')
	return HttpResponse(status=405)



class UserRegisterForm(View):
	form_class = UserRegisterForm
	template_name = 'register.html'

	def get(self, request):
		form = self.form_class(None)
		return render(request, self.template_name, {'form': form})

	def post(self, request):
		form = self.form_class(request.POST)

		if form.is_valid():
			user = User()
			user.username = form.cleaned_data['username']
			user.set_password(form.cleaned_data['password'])
			user.is_active = False # Need admin to activate
			user.save()

			author = Author()
			author.user = user
			author.host = 'http://' + request.get_host()

			# The id is the objects URI
			author.id = 'http://' + request.get_host() + '/author/' +\
			 			uuid.uuid4().hex

			# URL is the same as the id -- So says the Hindle
			author.url = author.id

			author.save()
			return render(request, "register_success.html")
		return render(request, self.template_name, {'form': form})



@login_required(login_url="login/")
@transaction.atomic
def update_profile(request):
	if request.method == 'POST':
		profile_form = ProfileForm(request.POST, instance=request.user.author)
		if profile_form.is_valid():
			profile_form.save()
			# TODO: send some verification message

			# TODO: should have an else: send some failure message. possibly
			# not needed.
	else:
		profile_form = ProfileForm(instance=request.user.author)
	return render(request, 'profile.html', {
		'profile_form': profile_form
	})


@login_required(login_url="login/")
def view_profile(request, id):
	if (request.method == 'GET'):
		host = request.GET.get('host', '')
		if (host != 'https://cmput404t06.herokuapp.com/dash/'):
			nodes = RemoteNode.objects.all()
			json_profile = {}
			for node in nodes:
				if (node.url == host):
					if (node.useauth):
						response = requests.get(node.url + "author/" + str(id), auth=HTTPBasicAuth(node.username, node.password))
					else:
						response = requests.get(node.url + "author/", auth=HTTPBasicAuth(node.username, node.password))

					json_profile = json.loads(response.content)
					break
			user = request.user
			request_id = user.author.id
			if not json_profile:
				return HttpResponse(status=404)
			else:
				json_profile['url'] = json_profile['host'] + 'author/' + str(json_profile['id'])
				return render(request, 'author.html', {'author': json_profile, 'user_id': request_id, 'request_user': user, 'profile_user': json_profile})
		else:
			author = Author.objects.get(id=id)
			display = Author.objects.get(id=id)
			user = request.user
			request_id = user.author.id
			author.url = author.host + 'author/' + str(author.id)
			return render(request, 'author.html', {'author':author, 'user_id':request_id,'request_user':user, 'profile_user':display })

	return HttpResponse(status=405)
