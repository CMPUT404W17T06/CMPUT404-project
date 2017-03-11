from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.views.generic import View
from django.db import transaction
from django.contrib import messages
from dash.models import Author

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
