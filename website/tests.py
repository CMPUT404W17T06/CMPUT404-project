from django.test import TestCase
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from dash.models import Author

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
