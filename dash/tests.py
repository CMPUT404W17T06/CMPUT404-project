from django.test import TestCase, Client
from django.test.utils import setup_test_environment
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.utils import IntegrityError
from dash.models import Author, Post, Comment, Category, Follow
from dash.forms import PostForm, CommentForm
from django.forms.models import model_to_dict
import requests
import uuid

# Create your tests here.

# https://docs.djangoproject.com/en/1.10/intro/tutorial05/
# https://docs.djangoproject.com/en/1.10/topics/testing/tools/
class DashViewTests(TestCase):
    def setUp(self):
        self.userCount = 0
        self.user = self.createUser()

        # Login by default, tests that need multiple users can logout
        self.client.login(username=self.user[1], password=self.user[2])

    def createUser(self):
        username = 'user{}'.format(self.userCount)
        password = 'pass{}'.format(self.userCount)

        user = User()
        user.username = username
        user.set_password(password)
        user.first_name = 'test_first{}'.format(self.userCount)
        user.last_name = 'test_last{}'.format(self.userCount)
        user.email = 'test{}@test.com'.format(self.userCount)
        user.is_active = True # This simulates activated user by admin
        user.save()

        author = Author()
        author.user = user
        author.github = 'https://github.com/user{}/'.format(self.userCount)
        author.host = 'http://testserver/'
        author.id = author.host + 'author/' + uuid.uuid4().hex
        author.url = author.id
        author.bio = 'I am {}'.format(user.get_full_name())
        author.save()

        # Increment user count
        self.userCount += 1

        return (user, username, password)
    
    def createFollow(self, author, friend, friendDisplayName):
        follow = Follow()
        follow.author = author
        follow.friend = friend
        follow.friendDisplayName = friendDisplayName
        follow.save()
        
    def createFriend(self, user1, user2):
    
        self.createFollow(user1.author, user2.author.id, user2.username)
        self.createFollow(user2.author, user1.author.id, user1.username)


    def test_index_view_with_no_posts(self):
        response = self.client.get('/dash/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No posts available.")
        self.assertQuerysetEqual(response.context['latest_post_list'], [])

    def make_post(self, **kwargs):
        data = {
            'title': 'Test',
            'description': 'Test',
            'contentType': 'text/plain',
            'content': 'Test',
            'visibility': 'PUBLIC'
        }
        data.update(kwargs) # Override with something from caller
        post_response = self.client.post("/dash/newpost/", data)
        self.assertEqual(post_response.status_code, 302)
        return data

    def test_make_post(self):
        data = self.make_post()

        response = self.client.get('/dash/')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.context['latest_post_list']),1)
        post = response.context['latest_post_list'][0]
        for i in data:
            self.assertEqual(post[i],data[i])

    def make_comment(self,post_id,author_id):
        data = {
            'comment': 'Test Comment',
            'post_id': post_id,
            'contentType': 'text/plain',
            'author': author_id
        }
        comment_response = self.client.post("/dash/newcomment/", data)
        self.assertEqual(comment_response.status_code, 302)
        del(data['post_id'])
        return data


    def test_comment_on_post(self):
        self.make_post()
        post_response = self.client.get('/dash/')

        post_id = post_response.context['latest_post_list'][0]['id']
        author_id = post_response.context["user"].author.id
        data = self.make_comment(post_id,author_id)

        response = self.client.get('/dash/')
        self.assertEqual(response.status_code, 200)

        responseCommentList = response.context['latest_post_list'][0]['comments']
        self.assertEqual(len(responseCommentList), 1,
                         'Post was missing comment')

        responseComment = responseCommentList[0]
        responseCommentContent = responseComment['comment']
        self.assertEqual(responseCommentContent, data['comment'])

        # Check if the authors are the same early because it's nested in the
        # response
        responseAuthorId = responseComment['author']['id']
        self.assertEqual(responseAuthorId, data['author'])

        del data['author']

        for i in data:
            self.assertEqual(responseComment[i], data[i])


    def test_private_post(self):
        """
        Test making a private post. Use first login to make a private post, then
        see if it is visible to a second user.
        """
        postData = self.make_post(visibility='PRIVATE')

        # Make sure the posting user can see this post
        response = self.client.get('/dash/')
        self.assertEqual(response.status_code, 200)
        postList = response.context['latest_post_list']
        self.assertEqual(len(postList), 1)
        responsePost = postList[0]
        for i in postData:
            self.assertEqual(responsePost[i], postData[i])

        # Logout and login on new user
        self.client.logout()
        user = self.createUser()
        self.client.login(username=user[1], password=user[2])

        # Make sure the new user can't see the post
        response = self.client.get('/dash/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['latest_post_list']), 0)

    def test_unlisted_post(self):
        """
        Test making an unlisted post. Use first login to make a private post, then
        see if it is visible to a second user.
        """
        # Post is public but unlisted
        postData = self.make_post(visibility = "UNLISTED")
        postData['visibility'] = 'PRIVATE'
        postData['unlisted'] = True

        # Make sure the posting user can see this post
        response = self.client.get('/dash/')
        self.assertEqual(response.status_code, 200)
        postList = response.context['latest_post_list']
        self.assertEqual(len(postList), 1)
        post = postList[0]
        for i in postData:
            self.assertEqual(post[i], postData[i], '{}: {} != {}'.format(i, post[i], postData[i]))

        # Logout and login on new user
        self.client.logout()
        user = self.createUser()
        self.client.login(username=user[1], password=user[2])

        # Make sure the new user can't see the post
        response = self.client.get('/dash/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['latest_post_list']), 0)

        # Build post direct link
        postUuid = post['id'].split('/')[-2]
        postPath = '/dash/posts/{}/'.format(postUuid)

        # Make sure the direct link works
        postOnlyResponse = self.client.get(postPath)
        self.assertEqual(postOnlyResponse.status_code, 200)

    def test_post_categories(self):
        """
        Test adding categories to a post.
        """
        categories = ['test category 1', 'test category 2']
        postData = self.make_post(categories=', '.join(categories))

        response = self.client.get('/dash/')
        self.assertEqual(response.status_code, 200)

        # Get Post
        postList = response.context['latest_post_list']
        post = postList[0]

        # Get categories
        postCats = post['categories']

        # Verify all categories on post are in what we wanted to set
        for cat in postCats:
            self.assertIn(cat, categories, 'Extra category set on post')

        # Verify all categories we wanted to set are on post
        for cat in categories:
            self.assertIn(cat, postCats, 'Missing category on post')
            
    def test_local_friend_post(self):
        # Post is FRIENDS
        user1 = self.createUser()
        self.client.login(username=user1[1], password=user1[2])

        postData = self.make_post(author = user1[0], visibility='FRIENDS')
                
        # Logout and login on new user
        self.client.logout()
        user2 = self.createUser()
        self.client.login(username=user2[1], password=user2[2])

        # Make sure the new user can't see the post
        response = self.client.get('/dash/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['latest_post_list']), 0)
        
        # Add friend.
        self.createFriend(user1[0], user2[0])
        
        #Now logged in user should see post.
        response = self.client.get('/dash/')
        self.assertEqual(response.status_code, 200)
        postList = response.context['latest_post_list']
        self.assertEqual(len(postList), 1)

    
