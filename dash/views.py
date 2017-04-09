# Author: Braedy Kuzma

from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_POST, require_GET
from django.views import generic
from .models import Post, Category, Comment, CanSee, Author, Follow, FriendRequest
from django.contrib.auth.models import User
from django.db.models import Q
from .forms import PostForm, CommentForm
import base64
import uuid
import itertools
from django.views.generic.edit import CreateView
from rest.authUtils import createBasicAuthToken, parseBasicAuthToken, \
                           getRemoteCredentials
from rest.models import RemoteCredentials
from rest.serializers import PostSerializer, CommentSerializer, \
                             FollowSerializer, AuthorSerializer
from django.utils.dateparse import parse_datetime
from urllib.parse import urlsplit, urlunsplit
import requests
from rest.verifyUtils import NotFound, RequestExists
import datetime

def postSortKey(postDict):
    return parse_datetime(postDict['published'])

def getFriends(authorID):
    friends = []
    try:
        #Check if author is local

        #AuthorTest checks if that query breaks, because if so that goes to the DNE except
        authorTest = Author.objects.get(id=authorID)

        #If it hasn't broken yet, just check if local friends.
        following = Follow.objects \
                               .filter(author=authorID) \
                               .values_list('friend', flat=True)

        for author in following:
            #Huzzah, now check if they follow you.
            following2 = Follow.objects \
                               .filter(author=author) \
                               .values_list('friend', flat=True)
            if authorID in following2:
                friends.append(author)


    except Author.DoesNotExist:
        #Huzzah, something broke. Most likely, this means that the author is remote
        following = []
        host = getRemoteCredentials(authorID)
        print("author is remote Detected")
        if not host:
            print("No Host detected")
            return friends
        print("Host Detected", host)
        
        r1 = requests.get(authorID+ 'friends/',
                          data={'query':'friends'},
                          auth=(host.username, host.password))
        if r1.status_code == 200:
            following = r1.json()['authors']
            print("Following:",following)
        
        for user in following:
            #THIS APPEARS TO BE WHERE THINGS BREAK
            #DUH, YOU DON"T CHECK IF THE SECond user is local
            print("Considering user in following, " , user)
            host2 = getRemoteCredentials(user)
            if not host2:
                #Might have friends with a server we don't have access to.
                print("Host2 not found")
                continue
            print("Host2 found ", host2)
            r2 = requests.get(user+ 'friends/',
                              data={'query':'friends'},
                              auth=(host.username, host.password))
            if r2.status_code == 200:
                following2 = r2.json()['authors']
                print("Following2:", following2)
                if authorID in following2:
                    friends.append(user)

    return friends

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


        #get local authors who follow you
        localFollowers = Follow.objects \
                               .filter(friend=self.request.user.author.id) \
                               .values_list('author', flat=True)
        #Of your local follwers, get those that you follow back, the "friends"

        localFriends = Follow.objects \
                             .filter(author=self.request.user.author.id,friend__in=localFollowers) \
                             .values_list('friend', flat=True)
        # Get posts marked FRIENDS visibility whose authors consider this author
        # a friend

        localFriendsPosts = Post.objects\
                           .filter(visibility='FRIENDS', author__in=localFriends,
                                     unlisted=False)
        #PURGE THE REMOTE POSTS

        following = Follow.objects \
                               .filter(author=self.request.user.author.id) \
                               .values_list('friend', flat=True)

        allLocalFOAFPosts = Post.objects\
                         .filter(visibility='FOAF', unlisted = False)
        localFOAFPosts = []
        for FOAFPost in allLocalFOAFPosts:
            friends = getFriends(FOAFPost.author.id)
            if self.request.user.author.id in friends:
                #Grab this post. Somehow.
                localFOAFPosts.append(FOAFPost)

            for friend in friends:
                FOAF = getFriends(friend)
                if self.request.user.author.id in FOAF:
                    #Grab this post. Somehow.
                    localFOAFPosts.append(FOAFPost)
                    break


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
                    #Check if you follow them.
                    if remotePost['author']['id'] in following:
                        #Huzzah, now check if they follow you.
                        host = getRemoteCredentials(remotePost['author']['id'])
                        r1 = requests.get(remotePost['author']['url']+ 'friends/',
                                          data={'query':'friends'},
                                          auth=(host.username, host.password))
                        if r1.status_code == 200:
                            friends = r1.json()['authors']
                            if self.request.user.author.id in friends:
                                remotePosts.append(remotePost)
                        else:
                            continue
                elif remotePost['visibility'] == 'FOAF':
                    #Same as above, if they're your friend you can just attach it.
                    theirFriends = getFriends(remotePost['author']['id'])
                    print("Post", remotePost)
                    print("Post author is", remotePost['author']['id'], remotePost['author']['displayName'])
                    print("You are:", self.request.user.author.id)
                    print("Post's Author's Friends:", theirFriends)
                   
                    if self.request.user.author.id in theirFriends:
                        #YOU ARE A FRIEND, JUST RUN WITH IT.
                        remotePosts.append(remotePost)
                    else:
                        #YOU ARE NOT A FRIEND, CHECK THEIR FRIENDS
                        for theirFriend in theirFriends:
                            theirFriendFriends = getFriends(theirFriend)
                            print("Post Author's Friend current viewing is:", theirFriend)
                            print("Post Author's Friend's Friends are:", theirFriendFriends)
                            if self.request.user.author.id in theirFriendFriends:
                                remotePosts.append(remotePost)
                                #YOU ARE A FOAF, SO BREAK OUT OF LOOP
                                break


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
        finalQuery = itertools.chain(localVisible, visibleToPosts, localFriendsPosts, localFOAFPosts)
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

        data['author'] = request.user.author
        data['host'] = host

        # Make new post
        post = Post()
        post.id = host + '/posts/' + uuid.uuid4().hex + '/'
        post.author = request.user.author
        post.save()

        # Did they upload an image?
        if 'attachImage' in request.FILES:
            makePost(post.id, data, request.FILES['attachImage'])
        else:
            makePost(post.id, data)

    # Redirect
    return redirect('dash:dash')


def makePost(pid, data, image=False):
    try:
        post = Post.objects.get(pk__contains=pid)
    except (Post.DoesNotExist, Post.MultipleObjectsReturned) as e:
        return redirect('dash:dash')

    # Fill in post
    post.title = data['title']
    post.contentType = data['contentType']
    post.content = data['content']
    post.visibility = data['visibility']
    post.unlisted = data['unlisted']
    post.description = data['description']
    post.save()

    if image:
        data['published'] = post.published
        makeImagePost(data, image)

    handlePostLists(post, data['categories'], data['visibleTo'])

def makeImagePost(data, image):
    # Build a bytes object from all of the image chunks (theoretically
    # only) one, but you never know
    b = bytes()
    for c in image.chunks():
        b += c

    # Encode it in b64
    encoded = base64.b64encode(b)
    encoded = encoded.decode('utf-8')

    # Turn it into a data url
    contentType = image.content_type + ';base64'
    encoded = 'data:' + contentType + ',' + encoded


    # Make the new post
    post = Post()
    imageId = uuid.uuid4().hex
    post.id = data['host'] + '/posts/' + imageId + '/'
    post.author = data['author']

    # Steal the parent post's title and description
    post.title = data['title'] + ' [IMAGE]'
    post.description = data['description']

    # Set up image content
    post.contentType = contentType
    post.content = encoded

    # Image posts are same Visibilty and unlisted-ness as parent post
    post.visibility = data['visibility']
    post.unlisted = data['unlisted']

    post.published = data['published'] - datetime.timedelta(microseconds=1)

    # Save the image post
    post.save()

    handlePostLists(post, data['categories'], data['visibleTo'])

def handlePostLists(post, categories, visibleTo):
    # Were there any categories?
    if categories:
        # Normalize the categories
        categoryList = categories.split(',')
        categoryList = [i.strip() for i in categoryList]

        # Build Category objects
        for categoryStr in categoryList:
            category = Category()
            category.category = categoryStr
            category.post = post
            category.save()

    if visibleTo:
        visibilityList = visibleTo.split(',')
        visibilityList = [i.strip() for i in visibilityList]

        # Build canSee objects
        for author in visibilityList:
            canSee = CanSee()
            canSee.visibleTo = author
            canSee.post = post
            canSee.save()

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

    # Is it a local post?
    hostAddress = urlsplit(data['post_id']).netloc
    userAddress = urlsplit(request.user.author.host).netloc
    if userAddress == hostAddress:
        # Save the new comment
        comment.save()
    else:
        # Post the new comment
        serialized_comment = CommentSerializer(comment).data

        # Try and ensure we have a decent URL
        hostUrl = data['post_id']
        if not (hostUrl.startswith('http://') or
                hostUrl.startswith('https://')):
            hostUrl = 'http://' + hostUrl

        # Get remote credentials for this host, just redirect if we fail I guess
        # TODO show error message on failure instead
        hostCreds = getRemoteCredentials(hostUrl)
        if hostCreds == None:
            print('Failed to find remote credentials for comment post: {}' \
                  .format(data['post_id']))
            return redirect('dash:dash')

        # Ensure that the last character is a slash
        if not hostUrl.endswith('/'):
            hostUrl += '/'

        hostUrl += 'comments/'
        data = {
            "query": "addComment",
            'post':data['post_id'],
            'comment':serialized_comment
        }
        r = requests.post(hostUrl,
                          auth=(hostCreds.username, hostCreds.password),
                          json=data)

    # Redirect to the dash
    return redirect('dash:dash')

@require_POST
@login_required(login_url="login")
def deletePost(request):
    # Get form data
    data = request.POST
    pid = data['post']
    try:
        post = Post.objects.get(pk__contains=pid)
    except (Post.DoesNotExist, Post.MultipleObjectsReturned) as e:
        return redirect('dash:manager')
    if post.author.id == request.user.author.id:
        post.delete()

    # Redirect to the manager
    return redirect('dash:manager')

@login_required(login_url="login")
def editPost(request, pid):
    if request.method == 'GET':
        pid = request.get_host() + '/posts/' + pid
        post = get_object_or_404(Post, pk__contains=pid)
        post = PostSerializer(post, many=False).data
        return JsonResponse(post)
    else:
        print(pid)
        form = PostForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            data['author'] = request.user.author
            data['host'] = 'http://' + request.get_host()
            # Did they upload an image?
            if 'attachImage' in request.FILES:
                makePost(pid, data, request.FILES['attachImage'])
            else:
                makePost(pid, data)
        return redirect('dash:manager')


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

        posts = PostSerializer(localVisible, many=True).data
        posts = sorted(posts, key = postSortKey, reverse=True)

        return posts

    def get_context_data(self, **kwargs):
        context = generic.ListView.get_context_data(self, **kwargs)
        context['postForm'] = PostForm()
        context['commentForm'] = CommentForm()
        return context

@login_required(login_url="login")
def post(request, pid):
    pid = request.get_host() + '/posts/' + pid
    post = get_object_or_404(Post, pk__contains=pid)
    post = PostSerializer(post, many=False).data
    return render(request, 'post_page.html', {'post':post})

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
        if 'accept' in request.POST and len(Follow.objects.filter(author=request.user.author, friend=request.POST['accept'])) == 0:
            follow = Follow()
            follow.author = request.user.author
            follow.friend = request.POST['accept']
            follow.friendDisplayName = request.POST['accept1']
            follow.save()
            '''if this is a local author we create another row in follow table
            if Author.objects.get(url = request.POST['accept'] && not Follow.objects.get( ):
                    follow = Follow()
                    follow.author = Author.objects.get(url = request.POST['accept'])
                    follow.friend = request.user.author.url
                    follow.requesterDisplayName = User.get_short_name(request.user)
                    follow.save()'''
            FriendRequest.objects.get(requestee = request.user.author,requester = request.POST['accept']).delete()
        elif 'reject' in request.POST:
            ''''if Author.objects.get(url = request.POST['accept']):
                    follow = Follow()
                    follow.author = Author.objects.get(url = request.POST['accept'])
                    follow.friend = request.user.author.url
                    follow.requesterDisplayName = User.get_short_name(request.user)
                    follow.save()'''
            FriendRequest.objects.get(requestee = request.user.author,requester = request.POST['reject']).delete()

    return render(request, 'friendrequests.html', {'followers': friend_requests})

@require_POST
@login_required(login_url="login")
def SendFriendRequest(request):
    # Get form data
    data = request.POST

    # Make friend request and follow
    friendrequest = FriendRequest()

    # Get author, all local users have an author except for the initial super
    # user. Just don't use them.
    author = request.user.author

    # Get the requested id
    requestedId = data['author']

    # check user trying to send request to self
    if requestedId == author.url:
        return redirect('dash:dash')

    # Check if this user is already following the requested user. If they aren't
    # then follow the user
    localFollows = Follow.objects.filter(author=author,
                                         friend=requestedId)
    if len(localFollows) == 0:
        # Build the follow
        follow = Follow()
        follow.friend = data['author']
        follow.friendDisplayName = data['displayName']
        follow.author = author
        follow.save()



    # Are they a local user?
    localAuthorRequested = None
    try:
        localAuthorRequested = Author.objects.get(id=requestedId)
        # User can't send a friend request if they are friends already, this avoid the problem
        # where users can spam others sending friend requests
        if len(Follow.objects.filter(author=author, friend=requestedId)) == 1 and len(
                Follow.objects.filter(author=Author.objects.get(url=requestedId), friend=author.url)):
            return redirect('dash:dash')

            # check if the friend is already the following requesting user, this avoid friend requests
            # being added into the table
        elif len(Follow.objects.filter(author=Author.objects.get(url=requestedId), friend=author.url)):
            return redirect('dash:dash')
    # If they aren't just leave it as None
    except Author.DoesNotExist:
        pass

    # Was the requested author local?
    if localAuthorRequested != None:
         # Don't duplicate friend requests
        localRequest = FriendRequest.objects \
                                    .filter(requestee=localAuthorRequested,
                                            requester=author.id)

        # Just redirect and pretend we did something
        if len(localRequest) > 0:
            return redirect('dash:dash')

        # Save the new friend request to local
        friendrequest.requester = author.id
        friendrequest.requestee = localAuthorRequested
        friendrequest.requesterDisplayName =  author.user.get_username()
        friendrequest.save()
    else:
        # Get remote credentials for this host, just redirect if we fail I guess
        # TODO show error message on failure instead
        hostCreds = getRemoteCredentials(requestedId)
        if hostCreds == None:
            print('Failed to find remote credentials for comment post: {}' \
                  .format(data['post_id']))
            return redirect('dash:dash')

        # Build remote friend request url
        url = hostCreds.host + 'friendrequest/'

        # Build request data
        authorData = AuthorSerializer(author).data
        requestedAuthor = {
            'id': requestedId,
            'url': requestedId,
            'host': data['host'],
            'displayName': data['displayName']
        }
        data = {
            "query": "friendrequest",
            'author': authorData,
            'friend': requestedAuthor
        }
        r = requests.post(url,
                          auth=(hostCreds.username, hostCreds.password),
                          json=data)
    #Redirect to the dash
    return redirect('dash:dash')

@login_required()
def DeleteFriends(request):
    #delete or unfollow friend, showing friend list and following list

    if request.method == 'POST':
        if 'unfriend' in request.POST:

            Follow.objects.get(friendDisplayName=request.POST['unfriend'],author=request.user.author).delete()

        elif 'unfollow' in request.POST:

            Follow.objects.get(friendDisplayName=request.POST['unfollow'],author=request.user.author).delete()
    Friends = []
    Followings = []
    #get all follow list
    following = request.user.author.follow.all()

    for follow in following:
        #check if B follows A
        localAuthorRequested = None
        try:
            localAuthorRequested = Author.objects.get(url = follow.friend)
    # If they aren't just leave it as None
        except Author.DoesNotExist:
            pass

    # Was the requested author local?
        if localAuthorRequested != None:
            if Follow.objects.filter(friend=follow.author.url,author=Author.objects.get(url = follow.friend)):
                friend = Follow.objects.filter(friend=follow.author.url,author=Author.objects.get(url = follow.friend))
                for f in friend:
                    Friends.append(f.author)
            else:
                Followings.append(follow.friendDisplayName)
        else:
            if Follow.objects.filter(friend=follow.author.url):
                friend = Follow.objects.filter(friend=follow.author.url)
                remote_friend_list=[]
                for f in friend:
                    #get f.author friend list
                    try:
                        host = getRemoteCredentials(f.author)
                        r1 = requests.get(f.author+ 'friends/',
                            data={'query':'friends'},
                            auth=(host.username, host.password))
                        if r1.status_code == 200:
                            remote_friend_list= r1.json()['authors']
                            if f.friendDisplayName in remote_friend_list:
                                Friends.append(f.author)
                    except:
                        Followings.append(follow.friendDisplayName)

    return render(request, 'following.html', {'Followings':Followings,'Friends':Friends})
