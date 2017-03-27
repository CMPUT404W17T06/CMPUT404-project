# Author: Braedy Kuzma

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_POST
from django.views import generic
from .models import Post, Category, Comment, CanSee, Author, Follow, FriendRequest
from django.db.models import Q
from .forms import PostForm, CommentForm
from .serializers import AuthorSerializer
import base64
import uuid
import itertools
from django.views.generic.edit import CreateView
from rest.authUtils import createBasicAuthToken, parseBasicAuthToken
from rest.models import RemoteCredentials
from rest.serializers import PostSerializer, CommentSerializer
from django.utils.dateparse import parse_datetime
from urllib.parse import urlsplit, urlunsplit
import requests

def postSortKey(postDict):
    return parse_datetime(postDict['published'])

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
        #list of all remote creditials we know about.
        #have host, username, password
        #does not contain our own server
        allRemotePosts = []
        hosts = RemoteCredentials.objects.all()
        for host in hosts:
            print('Getting from', host.host)
            # Technically, author/posts is all posts and posts/ is only PUBLIC
            # Will everyone follow that? who knows....
            r = requests.get(host.host + 'author/posts/',
                             data={'query':'posts'},
                             auth=(host.username, host.password))
            if r.status_code != 200:
                r = requests.get(host.host + 'posts/',
                                 data={'query':'posts'},
                                 auth=(host.username, host.password))
                if r.status_code != 200:
                    print('Error {} connecting while getting posts: {}'
                          .format(r.status_code, host.host))
                    print('Got response: {}'.format(r.text))
                    continue

            # Hacky things to make us work with remotes that follow the spec
            # "closely"
            posts = r.json()['posts']
            for post in posts:
                try:
                    uuid.UUID(post['id'])
                # If it fails it means it's (probably) a url
                except ValueError:
                    pass
                # If it succeeded we want to overwrite it with the url
                else:
                    origin = post['origin']
                    if origin[-1] != '/':
                        origin += '/'
                    post['id'] = origin
            allRemotePosts += posts

        # Get authors who consider this author a friend
        #friendOf = AuthorFriend.objects \
         #                      .filter(friendId=self.request.user.author.id) \
          #                     .values_list('friend1', flat=True)
        #friends=Author.objects.filter(followee__follower__user__username=self.request.user.username,followee__bidirectional=True)
        # Get posts marked FRIENDS visibility whose authors consider this author
        # a friend

        # friendsPosts = Post.objects\
        #                    .filter(visibility='FRIENDS', author__in=friends,
        #                             unlisted=False)
        #friendsPosts=Post.objects\
         #                   .filter(visibility='FRIENDS')\
          #                  .filter(author__followee__follower__user__username=self.request.user.username,author__followee__bidirectional=True)


        #PURGE THE REMOTE POSTS
        remotePosts=[]
        for remotePost in allRemotePosts:
            # Not in just default to False
            if 'unlisted' not in remotePost or remotePost['unlisted'] == False:
                # Not in, assume PUBLIC
                if 'visibility' not in remotePost:
                    remotePosts.append(remotePost)
                elif remotePost['visibility'] == 'PUBLIC':
                    remotePosts.append(remotePost)
                elif remotePost['visibility'] == 'FRIENDS':
                    #TODO: Do this later, oh my god.
                    pass
                elif remotePost['visibility'] == 'PRIVATE':
                    if self.request.user.author.url in remotePost['visibleTo']:
                        remotePosts.append(remotePost)


        # Get posts you can see
        authorCanSee = CanSee.objects \
                             .filter(visibleTo=self.request.user.author.url) \
                             .values_list('post', flat=True)
        visibleToPosts = Post.objects \
                             .filter(id__in=authorCanSee, visibility="PRIVATE",
                                        unlisted=False)

        #finalQuery = itertools.chain(localVisible, friendsPosts, visibleToPosts)
        finalQuery = itertools.chain(localVisible, visibleToPosts)
        postSerializer = PostSerializer(finalQuery, many=True)
        #postSerializer.data gives us a list of dicts that can be added to the remote posts lists
        posts= postSerializer.data + remotePosts
        posts = sorted(posts, key = postSortKey, reverse=True)

        return posts

    def get_context_data(self, **kwargs):
        context = generic.ListView.get_context_data(self, **kwargs)
        context['postForm'] = PostForm()
        context['commentForm'] = CommentForm()
        return context

@require_POST
@login_required(login_url="login")
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
            iPost.id = host + '/posts/' + imageId + '/'
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
        post.id = host + '/posts/' + uuid.uuid4().hex + '/'
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

        if data['visibleTo']:
            visibilityList = data['visibleTo'].split(',')
            visibilityList = [i.strip() for i in visibilityList]

            # Build Category objects
            for author in visibilityList:
                canSee = CanSee()
                canSee.visibleTo = author
                canSee.post = post
                canSee.save()

    # Redirect to the dash
    return redirect('dash:dash')


@require_POST
@login_required(login_url="login")
def newComment(request):
    # Get form data
    data = request.POST

    # Make new comment
    comment = Comment()

    # Fill in data
    comment.author = request.user.author.id
    comment.comment = data['comment']
    comment.contentType = data['contentType']
    comment.post_id = data['post_id']

    hostAddress = urlsplit(data['post_id']).netloc
    userAddress = urlsplit(request.user.author.host).netloc
    if userAddress == hostAddress:
        # Save the new comment
        comment.save()
    else:
        # Post the new comment
        serialized_comment = CommentSerializer(comment).data
        try:
            host = RemoteCredentials.objects.get(host__contains=hostAddress)
        except RemoteCredentials.DoesNotExist:
            return redirect('dash:dash')
        url = data['post_id'] + 'comments/'
        data = {
            "query": "addComment",
            'post':data['post_id'],
            'comment':serialized_comment
        }
        r = requests.post(url, auth=(host.username, host.password),json=data)

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

@login_required(login_url="login")
def post(request, pid):
    pid = request.get_host() + '/posts/' + pid
    post = get_object_or_404(Post, pk__contains=pid)
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

class ListFollowsAndFriends(LoginRequiredMixin, generic.ListView):
    ''' Lists whom you are following, who are following you and who are your friends '''
    
    context_object_name = 'following'
    template_name = 'following.html'

    def get_queryset(self):
        following = Follow.objects.filter(author=self.request.user.author)
        Friends = Follow.objects.filter(author=self.request.user.author)
        return {'Following':following,'Friends':Friends}

@login_required()
def friendRequest(request):
    ''' Accept or reject Friend requests '''
    friend_requests = FriendRequest.objects.filter(requestee = request.user.author)
    if request.method == 'POST':
        '''Accept will add a new row in follow and make them friends, then delete the friend request,
           this also checks if there are duplicate in follow table'''
        '''Reject will delete the friend request and do nothing to follow table'''
        if 'accept' in request.POST:
            follow = Follow()
            follow.author = request.user.author
            follow.friend = request.POST['accept']
            follow.requesterDisplayName = FriendRequest.objects.get(requesterDisplayName = request.POST['accept1']).requesterDisplayName
            follow.save()
            FriendRequest.objects.get(requestee = request.user.author,requester = request.POST['accept']).delete()
        elif 'reject' in request.POST:
            FriendRequest.objects.get(requestee = request.user.author,requester = request.POST['reject']).delete()
                
    return render(request, 'friendrequests.html', {'followers': friend_requests})    

@login_required()
def DeleteFriends(request):
    ''' Accept or reject Friend requests '''
    follow = Follow.objects.filter(author=request.user.author)
    Friends = Follow.objects.filter(author=request.user.author)
    if request.method == 'POST':
        if 'unfriend' in request.POST:
    
            Follow.objects.get(friend=request.POST['unfriend'],author=request.user.author).delete()

    return render(request, 'following.html', {'Following':follow,'Friends':Friends})

