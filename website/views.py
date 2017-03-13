from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.generic import View
from django.db import transaction

from dash.models import Author
from rest.models import RemoteNode
from .forms import ProfileForm, UserRegisterForm


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
@require_GET
def friend_requests(request):
	return render(request, 'requests.html')

@login_required(login_url="login/")
@require_GET
def friends(request):
	return render(request, 'friends.html')

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
			user.first_name = form.cleaned_data['firstName']
			user.last_name = form.cleaned_data['lastName']
			user.email = form.cleaned_data['email']
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
			author.username = form.cleaned_data['username']
			author.save()
			return render(request, "register_success.html")
		return render(request, self.template_name, {'form': form})



@login_required
@transaction.atomic
def update_profile(request):
	if request.method == 'POST':
		form = ProfileForm(request.POST)
		if form.is_valid():
			author = request.user.author
			author.github = form.cleaned_data.get('github', '')
			author.bio = form.cleaned_data.get('bio', '')
			author.save()

			user = request.user
			user.first_name = form.cleaned_data.get('first_name', '')
			user.last_name = form.cleaned_data.get('last_name', '')
			user.email = form.cleaned_data.get('email', '')

			# Check if password was set
			if form.cleaned_data['password']:
				# Note, this will log the user out
				user.set_password(form.cleaned_data['password'])
			
			user.save()

			return redirect('/profile/') # TODO No hardcoded redirects
	else:
		# Get initial datato fill into form
		user = request.user
		author = user.author
		init = {
			'github': author.github,
			'bio': author.bio,
			'last_name': user.last_name,
			'first_name': user.first_name,
			'email': user.email
		}

		# Make form with initial data
		profile_form = ProfileForm(init)
		return render(request, 'profile.html', {'profile_form': profile_form})


@login_required(login_url="login/")
@require_GET
def view_profile(request, id):
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
