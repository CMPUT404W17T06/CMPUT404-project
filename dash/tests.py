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
        u = 'test'
        p = '12345678'
        user = User()
        user.username = u
        user.set_password(p)
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
        author.username = u
        author.save()
        self.client.login(username=u, password=p)

    def test_index_view_with_no_posts(self):
        response = self.client.get('/dash/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No posts available.")
        self.assertQuerysetEqual(response.context['latest_post_list'], [])

    def test_make_post(self):
        data = {
            'title': 'Test',
            'description': 'Test',
            'contentType': 'Test',
            'content': 'Test',
            'visibility': 'PUBLIC'
        }
        post_response = self.client.post("/dash/newpost/", data)
        self.assertEqual(post_response.status_code, 302)

        response = self.client.get('/dash/')
        self.assertEqual(response.status_code, 200)

        post = model_to_dict(response.context['latest_post_list'][0])
        for i in data:
            self.assertEqual(post[i],data[i])

    def test_comment_on_post(self):
        pass

    def test_github_activity(self):
        """ Not certain of the best way to test this yet """
        #response = self.client.get('/dash/')
        #self.assertContains(response, "PushEvent")
