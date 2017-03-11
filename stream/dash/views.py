# Author: Braedy Kuzma

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views import generic
from .models import Post, Category, Comment, AuthorFriends
from django.db.models import Q
from .forms import PostForm, CommentForm

class StreamView(generic.ListView):
    template_name = 'dashboard.html'
    context_object_name = 'latest_post_list'
    def get_queryset(self):
        #Return the last five published questions
        querySet1 = Post.objects.filter(
            Q(visibility='PUBLIC') | Q(visibility='SERVERONLY') | Q(author=self.request.user.author)
        )
        querySet2 = Post.objects.filter(visibility = "FRIENDS")
        querySet3 = AuthorFriends.objects.filter(author = self.request.user.author)
        friendPost = []
        for p in querySet2:
            if querySet3.filter(friendId = p.author.id).exists():
                friendPost.append(p)
        querySet = list(querySet1)+friendPost
        return sorted(querySet, key=lambda Post: Post.published, reverse=True)[:5]
        #return querySet[:5]
        #return Post.objects.order_by('published')[:5]


    def get_context_data(self, **kwargs):
        context = generic.ListView.get_context_data(self, **kwargs)
        context['postForm'] = PostForm()
        context['commentForm'] = CommentForm()
        return context

@require_POST
@login_required(login_url="login/")
def newPost(request):
    # Get form data
    data = request.POST

    # Make new post
    post = Post()

    # Fill in data
    post.author = request.user.author
    post.title = data['title']
    post.contentType = data['contentType']
    post.content = data['content']
    post.visibility = data['visibility']

    # These both use the same URL because they're from us
    url = 'http://' + request.META['HTTP_HOST'] + '/posts/' + str(post.id)
    post.source = url
    post.origin = url

    # Not requred, use defaults in case
    post.description = data.get('description', default='')

    # Save the new post
    post.save()

    # Normalize the categories
    categoryList = data.get('categories', default='').split(',')
    categoryList = [i.strip() for i in categoryList]

    for categoryStr in categoryList:
        category = Category()
        category.category = categoryStr
        category.post = post
        category.save()

    # Redirect to the dash
    return redirect('dash:dash')


@require_POST
@login_required(login_url="login/")
def newComment(request):
    # Get form data
    data = request.POST

    # Make new comment
    comment = Comment()

    # Fill in data
    comment.author = request.user.author
    comment.comment = data['comment']
    comment.contentType = data['contentType']
    comment.post_id = data['post_id']

    # These both use the same URL because they're from us
    url = 'http://' + request.META['HTTP_HOST'] + '/comments/' + str(comment.id)
    comment.source = url
    comment.origin = url

    # Save the new post
    comment.save()

    # Redirect to the dash
    return redirect('dash:dash')

@login_required(login_url="login/")
def dashboard(request):
    return render(request,"dashboard.html")
