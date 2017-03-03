# Author: Braedy Kuzma

from rest_framework import serializers
from dash.models import Post

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('title', 'source', 'origin', 'description', 'contentType',
                  'content', 'author', 'categories')
