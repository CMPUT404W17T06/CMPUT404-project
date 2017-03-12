# this is actually importing views here, we might need to override these in the future
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login, logout
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect, render_to_response
from django.views.generic import View
from .forms import UserRegisterForm
from django.db import transaction
from .forms import ProfileForm

# Create your views here.
# this login required decorator is to not allow to any
# view without authenticating
def register_success(request):
	return render(request, "register_success.html")


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
	else:
		profile_form = ProfileForm(instance=request.user.author)
	return render(request, 'profile.html', {
		'profile_form': profile_form
	})

