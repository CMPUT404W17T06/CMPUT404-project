# Author: Braedy Kuzma

# Import views into our namespace so that importing views from this file works
# as normal
from .multiPostView import PostsView
from .singlePostView import PostView
from .commentView import CommentView
from .authorView import AuthorView
from .authorFriendsView import AuthorFriendsView, AuthorIsFriendsView
from .friendRequestView import FriendRequestView
