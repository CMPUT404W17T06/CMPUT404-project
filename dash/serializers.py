from rest_framework import serializers, pagination
from rest_framework.response import Response
from .models import Author
from django.contrib.auth.models import User

class AuthorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Author
        fields = ('id', 'host', 'displayName', 'url', 'github',
                  'email', 'firstName', 'lastName', 'bio')



class UserSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'last_login',
                  'author', 'date_joined', 'is_active')