# Author: Braedy Kuzma

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_POST
from django.views import generic
from .models import Post, Category, Comment, AuthorFriend, CanSee, FriendRequest
from django.db.models import Q
from .forms import PostForm, CommentForm
from .serializers import AuthorSerializer, FriendRequestSerializer
import base64
import uuid
import itertools

class StreamView(LoginRequiredMixin, generic.ListView):
    login_url = 'login'
    template_name = 'dashboard.html'
    context_object_name = 'latest_post_list'
    def get_queryset(self):
        # Return posts that are visible to everyone (Public, this server only,
        # self posted. Remove unlisted unless you are the creator of post)

        localVisible = Post.objects.filter(
            ((Q(visibility='PUBLIC') | Q(visibility='SERVERONLY'))\
             & Q(unlisted=False)) | Q(author=self.request.user.author)
        )

        # Get authors who consider this author a friend
        friendOf = AuthorFriend.objects \
                               .filter(friendId=self.request.user.author.id) \
                               .values_list('author', flat=True)
        # Get posts marked FRIENDS visibility whose authors consider this author
        # a friend
        friendsPosts = Post.objects\
                           .filter(visibility='FRIENDS', author__in=friendOf,
                                    unlisted=False)

        # Get posts you can see
        authorCanSee = CanSee.objects\
                             .filter(visibleTo=self.request.user.author.url) \
                             .values_list('post', flat=True)
        visibleToPosts = Post.objects \
                             .filter(id__in=authorCanSee, visibility="PRIVATE",
                                        unlisted=False)

        finalQuery = itertools.chain(localVisible, friendsPosts, visibleToPosts)
        return sorted(finalQuery, key=lambda post: post.published, reverse=True)

    def get_context_data(self, **kwargs):
        context = generic.ListView.get_context_data(self, **kwargs)
        context['postForm'] = PostForm()
        context['commentForm'] = CommentForm()
        return context

@require_POST
@login_required(login_url="login/")
def newPost(request):
    # Get form data
    form = PostForm(request.POST)
    if form.is_valid():
        data = form.cleaned_data

        host = 'http://' + request.get_host()
        # Did they upload an image?
        if 'attachImage' in request.FILES:
            # Build a bytes object from all of the image chunks (theoretically
            # only) one, but you never know
            image = request.FILES['attachImage']
            b = bytes()
            for c in image.chunks():
                b += c

            # Encode it in b64
            encoded = base64.b64encode(b)

            # Make the new post
            iPost = Post()
            imageId = uuid.uuid4().hex
            iPost.id = host + '/posts/' + imageId
            iPost.author = request.user.author

            # These are empty because they're just an extra post
            iPost.title = ''
            iPost.description = ''

            # Set up image content
            iPost.contentType = image.content_type + '; base64'
            iPost.content = encoded

            # Image posts are PRIVATE
            iPost.visibility = 'PRIVATE'

            # Image posts are unlisted
            iPost.unlisted = True

            # Save the image post
            iPost.save()

        # Make new post
        post = Post()

        # Fill in data
        post.id = host + '/posts/' + uuid.uuid4().hex
        post.author = request.user.author
        post.title = data['title']
        post.contentType = data['contentType']
        post.content = data['content']
        post.visibility = data['visibility']
        post.unlisted = data['unlisted']
        post.description = data['description']

        if 'attachImage' in request.FILES:
            post.content += '\n\n![' + post.title + '](' + host + '/dash/posts/' + imageId + ' "' + post.title + '")'

        # Save the new post
        post.save()

        # Were there any categories?
        if data['categories']:
            # Normalize the categories
            categoryList = data['categories'].split(',')
            categoryList = [i.strip() for i in categoryList]

            # Build Category objects
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


class ManagerView(LoginRequiredMixin, generic.ListView):
    login_url = 'login'
    template_name = 'manager.html'
    context_object_name = 'latest_post_list'
    def get_queryset(self):
        # Return posts that are visible to everyone (Public, this server only,
        # self posted)
        localVisible = Post.objects.filter(
            Q(author=self.request.user.author)
        )

        return sorted(localVisible, key=lambda post: post.published, reverse=True)

    def get_context_data(self, **kwargs):
        context = generic.ListView.get_context_data(self, **kwargs)
        context['postForm'] = PostForm()
        context['commentForm'] = CommentForm()
        return context

@require_POST
@login_required(login_url="login/")
def editPost(request):
    # Get form data
    form = PostForm(request.POST)
    if form.is_valid():
        data = form.cleaned_data

        host = 'http://' + request.get_host()
        # Did they upload an image?
        if 'attachImage' in request.FILES:
            # Build a bytes object from all of the image chunks (theoretically
            # only) one, but you never know
            image = request.FILES['attachImage']
            b = bytes()
            for c in image.chunks():
                b += c

            # Encode it in b64
            encoded = base64.b64encode(b)

            # Make the new post
            iPost = Post()
            imageId = uuid.uuid4().hex
            iPost.id = host + '/posts/' + imageId
            iPost.author = request.user.author

            # These are empty because they're just an extra post
            iPost.title = ''
            iPost.description = ''

            # Set up image content
            iPost.contentType = image.content_type + '; base64'
            iPost.content = encoded

            # Image posts are PRIVATE
            iPost.visibility = 'PRIVATE'

            # Image posts are unlisted
            iPost.unlisted = True

            # Save the image post
            iPost.save()

        # Make new post
        post = Post.objects.get(pk=data['post_id'])

        # Fill in data
        post.title = data['title']
        post.contentType = data['contentType']
        post.content = data['content']
        post.visibility = data['visibility']
        post.unlisted = data['unlisted']
        post.description = data['description']

        if 'attachImage' in request.FILES:
            post.content += '\n\n![' + post.title + '](' + host + '/dash/posts/' + imageId + ' "' + post.title + '")'

        # Save the new post
        post.save()

        # Were there any categories?
        if data['categories']:
            # Normalize the categories
            categoryList = data['categories'].split(',')
            categoryList = [i.strip() for i in categoryList]

            # Build Category objects
            for categoryStr in categoryList:
                category = Category()
                category.category = categoryStr
                category.post = post
                category.save()

    # Redirect to the dash
    return redirect('dash:dash')

@login_required(login_url="login/")
def post(request, pid):
    pid = 'http://' + request.get_host() + '/posts/' + pid
    post = get_object_or_404(Post, pk=pid)
    if 'base64' in post.contentType:
        return HttpResponse(base64.b64decode(post.content), content_type=post.contentType)
    return render(request, 'post.html', {'post':post})


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

def friend_handler(request):
    if (request.method == 'GET'):
        author = Author.objects.get(user_id=request.user.id)
        friends = author.friends.all()
        serializer = AuthorSerializer(friends, many=True)
        json_data = JSONRenderer().render(serializer.data)
        return HttpResponse(json_data, content_type='application/json')

    return HttpResponse(status=405)

def friend_handler_specific(request, id):
    if (request.method == 'DELETE'):
        author = Author.objects.get(user_id=request.user.id)

        try:
            friend = Author.objects.get(id=id)
            author.friends.remove(friend)
            return HttpResponse(status=200)

        except:
            return HttpResponse(status=404)

    elif (request.method == 'GET'):

        try :
            author = Author.objects.get(user_id=request.user.id)
            friend = author.friends.filter(id=id)[0]

            authors = [author.id]
            if (friend):
                authors.append(friend.id)
            obj = {
                'query': 'friends',
                'authors': authors,
            }

            json_data = json.dumps(obj)
            return HttpResponse(json_data, content_type='application/json')

        except:
            return HttpResponse(status=404)

    elif (request.method == 'POST'):
        try:
            author = Author.objects.get(id=id)
            json_body = json.loads(request.body)
            friends = map(lambda x:x.id, author.friends.filter(pk__in=json_body['authors']))

            obj = {
                'query': 'friends',
                'author': str(id),
                'authors': friends,
            }

            json_data = json.dumps(obj)
            return HttpResponse(json_data, content_type='application/json')

        except:
            return HttpResponse(status=404)

    return HttpResponse("")

def friend_query_handler(request, author1_id, author2_id):
    if (request.method == 'GET'):
        try:
            author1 = Author.objects.get(id=author1_id)
            author2 = Author.objects.get(id=author2_id)

            friends1 = author1.friends.filter(id=author2_id)
            friends2 = author2.friends.filter(id=author1_id)

            authors = [author1.id, author2.id]

            obj = {
                'query': 'friends',
                'authors': authors,
            }

            obj['friends'] = len(friends1) > 0 and len(friends2) > 0
            json_data = json.dumps(obj)

            return HttpResponse(json_data, content_type='application/json')


        except:
            # authors not found
            return HttpResponse(status=404)


# return friend request if exists, otherwise false
def friend_request_exists(author_id, friend_id):
    try:
        fr = FriendRequest.objects.get(requester_id=author_id, requestee_id=friend_id)
        return fr

    except:
        return False

def friendrequest_handler(request):

    if (request.method == 'POST'):
        # TODO: validation, are they already friends?
        body = json.loads(request.body)

        try:
            me = Author.objects.get(user_id=request.user.id)

        except:
            if (me.id != requester_id):
                return HttpResponse(status=401)

        try:
            me.friends.get(id=body['friend']['id'])
            return HttpResponse(status=409)
        except:
            pass

        fr = friend_request_exists(body['author']["id"], body['friend']['id'])

        if (fr):
            return HttpResponse(status=409)

        # try to get an existing reverse friend request (where the requester is the requestee)
        try:
            bidirectional = FriendRequest.objects.get(requestee_id=body['author']['id'], requester_id=body['friend']['id'])

            # exists a friend request from the other user, even if it was previously rejected
            # make users friends

            friend1 = Author.objects.get(id=bidirectional.requester.id)
            friend2 = Author.objects.get(id=bidirectional.requestee.id)


            if friend1.id != friend2.id:
                friend1.friends.add(friend2)
                friend2.friends.add(friend1)

            bidirectional.delete()

            return HttpResponse(status=201)


        except:
            fr = FriendRequest.objects.create(requester_id=body['author']['id'], requestee_id=body['friend']['id'])
            data = model_to_dict(fr)
            return create_json_response_with_location(data, fr.id, request.path)

    # return users list of pending requests
    elif (request.method == 'GET'):

        author = Author.objects.get(user_id=request.user.id)
        friend_requests = FriendRequest.objects.filter((Q(requestee_id=author.id) & Q(accepted__isnull=True)))
        for friend_request in friend_requests:
            setattr(friend_request, 'author', Author.objects.get(id=friend_request.requester_id))
            setattr(friend_request, 'friend', Author.objects.get(id=friend_request.requestee_id))

        serializer = FriendRequestSerializer(friend_requests, many=True)
        json_data = JSONRenderer().render(serializer.data)
        return HttpResponse(json_data, content_type='application/json')

    else:
        return HttpResponse(status=405)
