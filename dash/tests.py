from django.test import TestCase, Client
from django.test.utils import setup_test_environment
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.utils import IntegrityError
from dash.models import Author
import requests
import uuid

# Create your tests here.
u = 'test'
p = '12345678'

# https://docs.djangoproject.com/en/1.10/intro/tutorial05/
class DashViewTests(TestCase):
    def setUp(self):
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
        author.host = 'http://127.0.0.1/'
        author.id = 'http://127.0.0.1/author/' + uuid.uuid4().hex
        author.url = author.id
        author.username = u
        author.save()
        self.client.login(username=u, password=p)

    def test_index_view_with_no_posts(self):
        response = self.client.get('/dash/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No posts available.")
        self.assertQuerysetEqual(response.context['latest_post_list'], [])
