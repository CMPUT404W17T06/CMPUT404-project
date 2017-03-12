# Author: Braedy Kuzma

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views import generic
from .models import Post, Category, Comment, AuthorFriends, CanSee
from django.db.models import Q
from .forms import PostForm, CommentForm
from .serializers import AuthorSerializer

class StreamView(generic.ListView):
    template_name = 'dashboard.html'
    context_object_name = 'latest_post_list'
    def get_queryset(self):
        #Return the last five published questions
        querySet1 = Post.objects.filter(
            Q(visibility='PUBLIC') | Q(visibility='SERVERONLY') | Q(author=self.request.user.author)
        )
        postsVisFriends = Post.objects.filter(visibility = "FRIENDS")
        userFriends = AuthorFriends.objects.filter(author = self.request.user.author)
        friendPosts = []
        for p in postsVisFriends:
            if userFriends.filter(friendId = p.author.id).exists():
                friendPosts.append(p)
        
        postsVisPrivate = Post.objects.filter(visibility = "PRIVATE")
        privatePosts = []
        youCanSee = CanSee.objects.filter(visibleTo = self.request.user.author.url)
        #Turns out I can just do this. Huzzah.    
        for p in postsVisPrivate:
            if youCanSee.filter(post = p).exists():
                privatePosts.append(p)
            
        querySet = list(querySet1)+friendPosts+privatePosts
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

    # This post's origin is us. When we're serving it later we'll add the
    # source field based on where we got a post from
    url = 'http://' + request.META['HTTP_HOST'] + '/posts/' + str(post.id)
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

    # Save the new comment
    comment.save()

    # Redirect to the dash
    return redirect('dash:dash')

@login_required(login_url="login/")
def dashboard(request):
    return render(request,"dashboard.html")


def author_handler(request, id):
    #Return the foreign author's profile
    if (request.method == 'POST'):
        return HttpResponse(status=405)

    elif (request.method == 'GET'):
        author = Author.objects.get(id=id)
        author.friends = author.friends.all()
        author.url = author.host + 'author/' + str(author.id)
        serializer = AuthorSerializer(author)
        json_data = JSONRenderer().render(serializer.data)

        return HttpResponse(json_data, content_type='application/json')
