# Author: Braedy Kuzma

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views import generic
from .models import Post

class StreamView(generic.ListView):
    template_name = 'dashboard.html'
    context_object_name = 'latest_post_list'
    def get_queryset(self):
        #Return the last five published questions
        return Post.objects.order_by('published')[:5]

@login_required(login_url="login/")
def dashboard(request):
    return render(request,"dashboard.html")
