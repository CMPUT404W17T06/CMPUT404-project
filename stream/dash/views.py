# Author: Braedy Kuzma

from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views import generic
from .models import Post
from django.db.models import Q
from .forms import PostForm

class StreamView(generic.ListView):
    template_name = 'dashboard.html'
    context_object_name = 'latest_post_list'
    def get_queryset(self):
        #Return the last five published questions
        querySet = Post.objects.filter(
            Q(visibility='PUBLIC') | Q(visibility='SERVERONLY')
        )
        return querySet[:5]
        #return Post.objects.order_by('published')[:5]
        #CURRENTLY DOESNT DISPLAY ALL POSTS BY YOU FOR TESTING

    def get_context_data(self, **kwargs):
        context = generic.ListView.get_context_data(self, **kwargs)
        context['postForm'] = PostForm()
        return context

@login_required(login_url="login/")
@require_POST
def newPost(request):
    print(request)
    return HttpResponse(status=204)


@login_required(login_url="login/")
def dashboard(request):
    return render(request,"dashboard.html")
