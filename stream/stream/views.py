from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views import generic
from dash.models import Post

class StreamView(generic.ListView):
    template_name = 'stream.html'
    context_object_name = 'latest_post_list'
    def get_queryset(self):
        #Return the last five published questions
        #this is the only one used currently.
        #Posts.objects.filter(visibility='PUBLIC').order_by('published')[:5]
        return Post.objects.order_by('published')[:5]

def stream(request):
    latest_post_list = Post.objects.order_by('-published')[:5]
    context = {'latest_post_list': latest_post_list}
    return render(request, 'polls/index.html',context)


@login_required(login_url="login/")
def home(request):
    return render(request,"home.html")
