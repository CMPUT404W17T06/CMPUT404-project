from django.test import TestCase, Client
from django.test.utils import setup_test_environment
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.utils import IntegrityError
from dash.models import Author, Post, Comment
from dash.forms import PostForm, CommentForm
from django.forms.models import model_to_dict
import requests
import uuid

# Create your tests here.

# https://docs.djangoproject.com/en/1.10/intro/tutorial05/
# https://docs.djangoproject.com/en/1.10/topics/testing/tools/
class DashViewTests(TestCase):
    def setUp(self):
        username = 'test'
        password = '12345678'
        user = User()
        user.username = username
        user.set_password(password)
        user.first_name = 'test'
        user.last_name = 'test'
        user.email = 'test@test.com'
        user.is_active = True
        user.save()
        author = Author()
        author.user = user
        author.github = 'https://github.com/nshillin'
        author.host = 'http://127.0.0.1/'
        author.id = author.host + 'author/' + uuid.uuid4().hex
        author.url = author.id
        author.username = username
        author.save()
        self.client.login(username=username, password=password)

    def test_index_view_with_no_posts(self):
        response = self.client.get('/dash/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No posts available.")
        self.assertQuerysetEqual(response.context['latest_post_list'], [])

    def make_post(self):
        data = {
            'title': 'Test',
            'description': 'Test',
            'contentType': 'text/plain',
            'content': 'Test',
            'visibility': 'PUBLIC'
        }
        post_response = self.client.post("/dash/newpost/", data)
        self.assertEqual(post_response.status_code, 302)
        return data

    def test_make_post(self):
        data = self.make_post()

        response = self.client.get('/dash/')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.context['latest_post_list']),1)
        post = model_to_dict(response.context['latest_post_list'][0])
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

        post_id = post_response.context['latest_post_list'][0].id
        author_id = post_response.context["user"].author.id
        data = self.make_comment(post_id,author_id)

        response = self.client.get('/dash/')
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "Test Comment")

        comment = model_to_dict(response.context['latest_post_list'][0].comment_set.all()[0])
        for i in data:
            self.assertEqual(comment[i],data[i])


    def test_github_activity(self):
        """ Not certain of the best way to test this yet """
        #response = self.client.get('/dash/')
        #self.assertContains(response, "PushEvent")
