from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views import generic

@login_required(login_url="login/")
def home(request):
    return render(request,"home.html")
