from django.test import TestCase
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from dash.models import Author
import uuid

# Create your tests here.

class WebsiteViewTests(TestCase):
    def setUp(self):
        self.userCount = 0

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
        author.github = 'https://github.com/user{}'.format(self.userCount)
        author.host = 'http://127.0.0.1/'
        author.id = author.host + 'author/' + uuid.uuid4().hex
        author.url = author.id
        author.bio = 'I am {}'.format(user.get_full_name())
        author.save()

        # Increment user count
        self.userCount += 1

        return (user, username, password)

    def test_register(self):
        data = {
            'firstName': 'first1',
            'lastName': 'last1',
            'email': 'email@email.com',
            'username': 'testuser',
            'password': 'password',
            'password2': 'password'
        }
        register_response = self.client.post("/login/register/", data)
        self.assertEqual(register_response.status_code,
                         200,
                         'Bad register status code')

        users = User.objects.all()
        self.assertEqual(len(users), 1, 'More than one user exists')
        user = users[0]

        # Verify all fields we can (password can't be verified by text)
        self.assertEqual(user.username,
                         data['username'],
                         'Bad username on register')
        self.assertEqual(user.last_name,
                         data['lastName'],
                         'Bad last name on register')
        self.assertEqual(user.first_name,
                         data['firstName'],
                         'Bad first name on register')
        self.assertEqual(user.email,
                         data['email'],
                         'Bad email on register')

        # Verify an author was created for this user
        try:
            author = user.author
        except django.db.models.fields.related_descriptors.RelatedObjectDoesNotExist:
            assertTrue(False, 'Author did not exist')

        # Try logging in
        success = self.client.login(username=data['username'],
                                    password=data['password'])
        self.assertFalse(success, 'Succeeded logging in before active')

        # Activate the user, like an admin accepting an author
        user.is_active = True
        user.save()

        success = self.client.login(username=data['username'],
                                    password=data['password'])
        self.assertTrue(success, 'Could not login after active')

    def test_update_profile(self):
        user, name, password = self.createUser()
        self.assertTrue(self.client.login(username=name, password=password),
                        'Could not login')
        data = {
            'github': 'http://github.com/updated',
            'bio': 'updated bio',
            'first_name': 'Updated',
            'last_name': 'Updated',
            'email': 'updated@updated.com',
            'password': 'updated',
            'password2': 'updated'
        }

        # Post the update
        update_response = self.client.post("/profile/", data)
        self.assertEqual(update_response.status_code,
                         302,
                         'Bad update status code')

        # Make sure we didn't make any more objects
        users = User.objects.all()
        self.assertEqual(len(users), 1, 'Update created new object')

        # Get updated user
        user = users[0]

        # Make sure user fields were updated, except password
        self.assertEqual(user.last_name,
                         data['last_name'],
                         'Bad last name on update')
        self.assertEqual(user.first_name,
                         data['first_name'],
                         'Bad first name on update')
        self.assertEqual(user.email,
                         data['email'],
                         'Bad email on update')

        # Make sure author fields were updated
        author = user.author
        self.assertEqual(author.bio,
                         data['bio'],
                         'Bad bio on update')
        self.assertEqual(author.github,
                         data['github'],
                         'Bad github on update')

        # Try getting dash, should redirect to login because changing our
        # password logs us out
        dash_response = self.client.get('/dash/')
        self.assertEqual(dash_response.status_code, 302,
                         'User was not logged out after password change')
        self.assertEqual(dash_response.url, '/login/?next=/dash/',
                         'Login redirect incorrect')

        # Make sure we can login with our new password
        self.assertTrue(self.client.login(username=user,
                                          password=data['password']),
                        'Could not login')
