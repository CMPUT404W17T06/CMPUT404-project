from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.views.generic import View
from django.db import transaction
from django.contrib import messages
from dash.models import Author, Nodes
from .forms import ProfileForm
from .forms import UserRegisterForm

import requests
import json
from requests.auth import HTTPBasicAuth

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
			user = form.save(commit=False)

			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			user.set_password(password)
			user.is_active = False
			user.save()

			user = authenticate(username=username, password=password)
			if user is not None:
				if user.is_active:
					login(request, user)
					return render(request, "home.html")
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
		if (host != 'https://cmput404t02.herokuapp.com/service/'):
			nodes = Nodes.objects.all()
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




